variable "project_name" {
  type        = string
  description = "Nombre del proyecto"
}

variable "environment" {
  type        = string
  description = "Entorno"
}

variable "backend_public_dns" {
  type        = string
  description = "El DNS público del host EC2 del backend Django"
}
