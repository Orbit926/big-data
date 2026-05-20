output "vpc_id" {
  description = "ID de la VPC creada"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Lista de IDs de las subnets públicas creadas"
  value       = aws_subnet.public[*].id
}
