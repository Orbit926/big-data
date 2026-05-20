output "cloudfront_domain_name" {
  description = "El dominio generado de CloudFront para acceder a la aplicación"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "s3_bucket_name" {
  description = "El nombre del bucket S3 creado"
  value       = aws_s3_bucket.frontend.id
}
