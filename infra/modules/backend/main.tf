# ─────────────────────────────────────────────────────────────────────────────
# ECR: Registro para la imagen Docker del backend
# ─────────────────────────────────────────────────────────────────────────────
resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}-${var.environment}-backend"
  image_tag_mutability = "MUTABLE"
  force_delete         = true # Permite borrar el repo con tofu destroy aunque tenga imágenes

  image_scanning_configuration {
    scan_on_push = false
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-ecr"
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# ECS Cluster
# ─────────────────────────────────────────────────────────────────────────────
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-cluster"
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# LOG GROUP: Para capturar logs del backend en CloudWatch
# ─────────────────────────────────────────────────────────────────────────────
resource "aws_cloudwatch_log_group" "ecs_backend" {
  name              = "/ecs/${var.project_name}-${var.environment}-backend"
  retention_in_days = 7
}

# ─────────────────────────────────────────────────────────────────────────────
# SECURITY GROUPS
# ─────────────────────────────────────────────────────────────────────────────
resource "aws_security_group" "ecs_host" {
  name        = "${var.project_name}-${var.environment}-ecs-host-sg"
  description = "Security Group para el host EC2 de ECS"
  vpc_id      = var.vpc_id

  # Puerto 8000: Permite llamadas a la API de Django desde cualquier origen (para MVP con CORS = *)
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Puerto 22: SSH (útil para ingresar y debugear en el MVP)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Salida libre a internet para descargar paquetes y jalar imágenes de ECR
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-host-sg"
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# ROLES DE IAM Y PERMISOS
# ─────────────────────────────────────────────────────────────────────────────

# 1. Rol para la Instancia de EC2 (El agente de ECS lo requiere para registrarse y descargar imágenes)
resource "aws_iam_role" "ecs_instance_role" {
  name = "${var.project_name}-${var.environment}-ecs-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "ec2.amazonaws.com" }
      }
    ]
  })
}

# Adjuntar política predefinida por AWS para ECS Container Host en EC2
resource "aws_iam_role_policy_attachment" "ecs_instance_policy" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "${var.project_name}-${var.environment}-ecs-instance-profile"
  role = aws_iam_role.ecs_instance_role.name
}

# 2. Rol de Ejecución de Tareas (Para que ECS descargue imágenes y mande logs a CloudWatch)
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-${var.environment}-ecs-task-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "ecs-tasks.amazonaws.com" }
      }
    ]
  })
}

# Adjuntar política oficial de ejecución de tareas
resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ─────────────────────────────────────────────────────────────────────────────
# INSTANCIA EC2 (El servidor fijo)
# ─────────────────────────────────────────────────────────────────────────────

# Buscar dinámicamente la última AMI oficial optimizada para ECS en Amazon Linux 2
data "aws_ssm_parameter" "ecs_optimized_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id"
}

resource "aws_instance" "ecs_host" {
  ami                  = data.aws_ssm_parameter.ecs_optimized_ami.value
  instance_type        = var.instance_type
  subnet_id            = var.public_subnet_ids[0] # Levantar en la primera subnet pública
  iam_instance_profile = aws_iam_instance_profile.ecs_instance_profile.name
  security_groups      = [aws_security_group.ecs_host.id]

  # Registrar la máquina en el Clúster de ECS y pre-crear el archivo SQLite vacío
  # para que Docker lo monte como archivo en lugar de directorio.
  user_data = <<-EOF
              #!/bin/bash
              echo ECS_CLUSTER=${aws_ecs_cluster.main.name} >> /etc/ecs/ecs.config
              mkdir -p /var/lib/django-db
              touch /var/lib/django-db/db.sqlite3
              chmod 777 /var/lib/django-db/db.sqlite3
              EOF

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-host"
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# ELASTIC IP (IP estática y fija)
# ─────────────────────────────────────────────────────────────────────────────
resource "aws_eip" "backend_ip" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-backend-eip"
  }
}

# Asociar la IP estática con nuestra instancia EC2
resource "aws_eip_association" "eip_assoc" {
  instance_id   = aws_instance.ecs_host.id
  allocation_id = aws_eip.backend_ip.id
}

# ─────────────────────────────────────────────────────────────────────────────
# ECS TASK DEFINITION Y SERVICIO (EC2 Launch Type)
# ─────────────────────────────────────────────────────────────────────────────

# Volumen persistente en el host apuntando al archivo SQLite
resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.project_name}-${var.environment}-backend-task"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]

  # Definición del contenedor
  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "${aws_ecr_repository.backend.repository_url}:latest"
      cpu       = 256  # 0.25 vCPU
      memory    = 450  # 450 MB (perfecto para un host de 1GB de RAM)
      essential = true

      portMappings = [
        {
          hostPort      = 8000
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      mountPoints = [
        {
          sourceVolume  = "sqlite_db"
          containerPath = "/app/db.sqlite3"
          readOnly      = false
        }
      ]

      environment = [
        { name = "DEBUG", value = "True" },
        { name = "ALLOWED_HOSTS", value = "*" },
        { name = "CORS_ALLOW_ALL_ORIGINS", value = "True" }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_backend.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "backend"
        }
      }
    }
  ])

  # Volumen del host que apunta al archivo db.sqlite3 creado por el user_data
  volume {
    name      = "sqlite_db"
    host_path = "/var/lib/django-db/db.sqlite3"
  }
}

# ECS Service para correr nuestra tarea en el clúster EC2
resource "aws_ecs_service" "backend" {
  name            = "${var.project_name}-${var.environment}-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "EC2"

  # Evita problemas de puertos duplicados al actualizar el servicio
  # bajando la tarea antigua antes de arrancar la nueva (1 réplica fija)
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  depends_on = [
    aws_instance.ecs_host
  ]
}
