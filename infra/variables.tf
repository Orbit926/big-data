variable "aws_region" {
  type        = string
  description = "Región de AWS donde se desplegarán los recursos"
  default     = "us-east-1"
}

variable "aws_profile" {
  type        = string
  description = "El perfil de AWS configurado localmente en ~/.aws/credentials para realizar el despliegue"
  default     = "default"
}


variable "project_name" {
  type        = string
  description = "Nombre general del proyecto (usado para nombrar los recursos)"
  default     = "move-mvp"
}

variable "environment" {
  type        = string
  description = "Entorno actual del despliegue (ej. dev, staging, prod)"
  default     = "dev"
}

variable "instance_type" {
  type        = string
  description = "Tipo de instancia de EC2 para ECS (ej. t3.micro, t4g.nano)"
  default     = "t3.micro"
}
