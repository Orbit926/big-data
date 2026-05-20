variable "project_name" {
  type        = string
  description = "Nombre del proyecto"
}

variable "environment" {
  type        = string
  description = "Entorno"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block para la VPC"
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks para las subnets públicas"
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}
