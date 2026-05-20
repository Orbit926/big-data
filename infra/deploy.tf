# ─────────────────────────────────────────────────────────────────────────────
# AUTOMATIZACIÓN DE DESPLIEGUE (CI/CD Local con OpenTofu)
# ─────────────────────────────────────────────────────────────────────────────

# 1. Compilar y Subir la imagen Docker del backend a ECR y forzar actualización de ECS
resource "null_resource" "build_and_push_backend" {
  triggers = {
    # Se ejecuta si cambia la URL del repositorio ECR o si forzamos el despliegue
    ecr_url = module.backend.ecr_repository_url
  }

  provisioner "local-exec" {
    command = <<-EOT
      echo "============================================================="
      echo "🚀 INICIANDO AUTOMATIZACIÓN DE DESPLIEGUE DEL BACKEND (ECR/ECS)"
      echo "============================================================="
      
      echo "🔑 Iniciando sesión en AWS ECR..."
      aws ecr get-login-password --region ${var.aws_region} --profile ${var.aws_profile} | docker login --username AWS --password-stdin ${module.backend.ecr_repository_url}
      
      echo "🐳 Construyendo la imagen Docker del backend para la plataforma linux/amd64..."
      docker build --platform linux/amd64 -t ${module.backend.ecr_repository_url}:latest ../backend
      
      echo "📤 Subiendo la imagen Docker a AWS ECR..."
      docker push ${module.backend.ecr_repository_url}:latest
      
      echo "🔄 Forzando redespliegue de la tarea en ECS..."
      aws ecs update-service \
        --cluster ${module.backend.ecs_cluster_name} \
        --service ${module.backend.ecs_service_name} \
        --force-new-deployment \
        --region ${var.aws_region} \
        --profile ${var.aws_profile}
        
      echo "✅ ¡Backend desplegado y actualizado con éxito en ECS!"
      echo "============================================================="
    EOT
  }

  depends_on = [module.backend]
}

# 2. Inyectar IP del backend, compilar React y subir el frontend estático a S3
resource "null_resource" "build_and_push_frontend" {
  triggers = {
    # Se ejecuta de forma automática si cambia la IP del backend o el bucket S3 de destino
    backend_ip = module.backend.backend_public_ip
    s3_bucket  = module.frontend.s3_bucket_name
  }

  provisioner "local-exec" {
    command = <<-EOT
      echo "============================================================="
      echo "🚀 INICIANDO AUTOMATIZACIÓN DE DESPLIEGUE DEL FRONTEND (S3/CF)"
      echo "============================================================="
      
      echo "📂 Entrando al directorio del frontend..."
      cd ../frontend
      
      echo "📝 Configurando API URL en .env.production (VITE_API_URL = vacío para rutas relativas)..."
      echo "VITE_API_URL=" > .env.production
      
      echo "📦 Instalando dependencias del frontend..."
      npm install
      
      echo "🏗️ Compilando la aplicación React para producción..."
      npm run build
      
      echo "📤 Sincronizando compilación con el bucket S3 de AWS..."
      aws s3 sync dist/ s3://${module.frontend.s3_bucket_name} --delete --profile ${var.aws_profile}
      
      echo "✅ ¡Frontend compilado y subido con éxito a S3!"
      echo "============================================================="
    EOT
  }

  depends_on = [module.backend, module.frontend]
}
