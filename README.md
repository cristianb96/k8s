# Sistema de Pedidos - Helm + Argo CD

Este repositorio contiene:

- Backend Python (FastAPI) con conexión a PostgreSQL
- Chart de Helm (`charts/pedidos`) que empaqueta backend + PostgreSQL (Bitnami)
- Manifiesto de Argo CD (`argocd/application-pedidos.yaml`) para CD

## Prerrequisitos

- Docker
- Kubernetes (kind/minikube/AKS/EKS/GKE)
- Helm 3
- Argo CD instalado en el clúster (namespace `argocd`)

## Backend

### Opción 1: GitHub Container Registry (recomendado)

El repositorio incluye GitHub Actions que construye y publica automáticamente la imagen en `ghcr.io`:

- La imagen se publica en: `ghcr.io/cristianb96/k8s/pedidos-backend`
- Se activa en push a `main` o `develop` cuando cambian archivos en `backend/`

### Opción 2: Construcción manual

```bash
# Desde la raíz del repo
docker build -t ghcr.io/cristianb96/k8s/pedidos-backend:0.1.0 -f backend/Dockerfile .
docker push ghcr.io/cristianb96/k8s/pedidos-backend:0.1.0
```

## Despliegue con Helm (local)

### Despliegue básico

```bash
helm dependency update charts/pedidos
helm install pedidos charts/pedidos
```

### Despliegue con configuración personalizada

```bash
helm install pedidos charts/pedidos \
  --set backend.image.repository=ghcr.io/cristianb96/k8s/pedidos-backend \
  --set backend.image.tag=v1.0.0 \
  --set backend.replicaCount=3 \
  --set db.auth.password=mi-password-seguro \
  --set backend.resources.limits.memory=512Mi
```

### Usar archivo de valores personalizado

```bash
# Copia y edita el archivo de ejemplo
cp charts/pedidos/values-example.yaml charts/pedidos/values-custom.yaml
# Edita values-custom.yaml según tus necesidades
helm install pedidos charts/pedidos -f charts/pedidos/values-custom.yaml
```

Probar:

```bash
kubectl get pods
kubectl port-forward svc/pedidos-pedidos 8080:80
curl http://localhost:8080/healthz
```

## Ingress (opcional)

Edita `values.yaml` y habilita `backend.ingress.enabled: true` y configura host.

## Despliegue con Argo CD

El manifiesto ya está configurado para usar tu repositorio de GitHub. Solo aplica:

```bash
kubectl apply -f argocd/application-pedidos.yaml
```

La app quedará en el proyecto `default`, namespace `pedidos`.

### Configuración de Argo CD

1. Asegúrate de que Argo CD puede acceder a tu repositorio (público o con credenciales)
2. La imagen se actualizará automáticamente cuando hagas push a `main`
3. Puedes ver el estado en la UI de Argo CD: `kubectl port-forward svc/argocd-server -n argocd 8080:443`

## Estructura del Chart

El chart principal `pedidos` contiene dos subcharts:

### Subchart `db`

- Usa el chart oficial de Bitnami PostgreSQL
- Configurado en `charts/pedidos/charts/db/`
- Valores en `values.yaml` bajo la sección `db:`

### Subchart `backend`

- Deployment, Service, ConfigMap e Ingress del backend FastAPI
- Configurado en `charts/pedidos/charts/backend/`
- Valores en `values.yaml` bajo la sección `backend:`

## Recursos Kubernetes Obligatorios

### 1. **Deployment** → Backend

- Despliega el backend FastAPI
- Configuración de réplicas, recursos y health checks
- Variables de entorno desde ConfigMap y Secret

### 2. **Service** → ClusterIP

- Expone el backend dentro del cluster
- Tipo ClusterIP para comunicación interna
- Puerto 80 → 8000 (backend)

### 3. **Ingress** → `/api/*` → Backend

- Ruta `/api/*` redirige al backend
- Configuración de TLS opcional
- Anotaciones personalizables

### 4. **PersistentVolumeClaim** → Datos de BD

- Almacenamiento persistente para PostgreSQL
- Configuración de tamaño y clase de almacenamiento
- Modo de acceso ReadWriteOnce

### 5. **ConfigMap** → Configuración no sensible

- Variables de entorno no sensibles del backend
- Configuración de base de datos (host, puerto, nombre)
- Configuración de aplicación (log level, debug, etc.)

### 6. **Secret** → Credenciales de BD

- Contraseñas y URLs de conexión sensibles
- DATABASE_URL completa con credenciales
- Contraseña de base de datos por separado

## Variables Configurables

### Imagen y Tag

```yaml
# Backend
backend:
  image:
    repository: ghcr.io/cristianb96/k8s/pedidos-backend
    tag: "latest"
    pullPolicy: IfNotPresent

# Base de datos
db:
  image:
    repository: bitnami/postgresql
    tag: "15.5.0"
    pullPolicy: IfNotPresent
```

### Credenciales de Base de Datos

```yaml
db:
  auth:
    username: pedidos
    password: pedidospass
    database: pedidos
    existingSecret: "" # Usar secret existente
```

### Réplicas

```yaml
# Backend
backend:
  replicaCount: 1

# Base de datos
db:
  replicaCount: 1
```

### Recursos (CPU/Memoria)

```yaml
# Backend
backend:
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "200m"

# Base de datos
db:
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

### Autoscaling (Backend)

```yaml
backend:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
```

### Persistencia (Base de Datos)

```yaml
db:
  persistence:
    enabled: true
    size: 1Gi
    storageClass: "fast-ssd"
    accessMode: ReadWriteOnce
```

## Variables y secretos

- `DATABASE_URL` se inyecta vía `ConfigMap` generado por el chart principal
- La comunicación entre subcharts se maneja automáticamente
- Puedes desactivar `db.enabled` y configurar una BD externa si es necesario
- Ver `values-example.yaml` para ejemplos completos de configuración

## Endpoints

- `GET /healthz`
- `GET /db/health`
- `GET /orders`
- `POST /orders?customer=ACME&item=Widget&quantity=2`
