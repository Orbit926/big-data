variable "vpc_id" {
  type        = string
  description = "ID de la VPC común"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "Lista de IDs de las subnets públicas creadas en la red"
}

variable "project_name" {
  type        = string
  description = "Nombre del proyecto"
}

variable "environment" {
  type        = string
  description = "Entorno"
}

variable "instance_type" {
  type        = string
  description = "Tipo de instancia de EC2 para correr ECS (t3.micro, t4g.nano, etc.)"
  default     = "t3.micro"
}
