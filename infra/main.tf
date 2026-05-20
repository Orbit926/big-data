# ─────────────────────────────────────────────────────────────────────────────
# 1. Módulo de Red (VPC, Subnets Públicas, Internet Gateway, Ruteo)
# ─────────────────────────────────────────────────────────────────────────────
module "network" {
  source       = "./modules/network"
  project_name = var.project_name
  environment  = var.environment
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. Módulo de Frontend (S3 Bucket, CloudFront Distribution y OAC)
# ─────────────────────────────────────────────────────────────────────────────
module "frontend" {
  source             = "./modules/frontend"
  project_name       = var.project_name
  environment        = var.environment
  backend_public_dns = module.backend.backend_public_dns
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. Módulo de Backend (ECR, ECS en EC2 Único, Elastic IP, SQLite EBS Volume)
# ─────────────────────────────────────────────────────────────────────────────
module "backend" {
  source            = "./modules/backend"
  vpc_id            = module.network.vpc_id
  public_subnet_ids = module.network.public_subnet_ids
  project_name      = var.project_name
  environment       = var.environment
  instance_type     = var.instance_type
}
