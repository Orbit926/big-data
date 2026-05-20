output "backend_ecr_repository_url" {
  description = "URL del repositorio de ECR para subir la imagen Docker del backend"
  value       = module.backend.ecr_repository_url
}

output "backend_public_ip" {
  description = "IP Pública Estática (Elastic IP) del backend. Úsala en la configuración del frontend."
  value       = module.backend.backend_public_ip
}

output "frontend_cloudfront_domain_name" {
  description = "Dominio de CloudFront para acceder al frontend en producción"
  value       = module.frontend.cloudfront_domain_name
}

output "frontend_s3_bucket_name" {
  description = "Nombre del Bucket de S3 para subir los archivos estáticos del frontend"
  value       = module.frontend.s3_bucket_name
}
