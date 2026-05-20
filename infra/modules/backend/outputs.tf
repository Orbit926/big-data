output "ecr_repository_url" {
  description = "URL de ECR para subir la imagen del backend"
  value       = aws_ecr_repository.backend.repository_url
}

output "backend_public_ip" {
  description = "La IP pública fija asignada al backend (Elastic IP)"
  value       = aws_eip.backend_ip.public_ip
}

output "ecs_cluster_name" {
  description = "Nombre del Clúster de ECS"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Nombre del Servicio de ECS"
  value       = aws_ecs_service.backend.name
}

output "backend_public_dns" {
  description = "El DNS público del host EC2 del backend"
  value       = aws_instance.ecs_host.public_dns
}

