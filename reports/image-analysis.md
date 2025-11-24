# Image Analysis Report — app-notas:1.0

Este informe documenta el análisis de la imagen `app-notas:1.0` utilizando las herramientas **Dive** y **Trivy**, junto con verificaciones relacionadas a seguridad, tamaño y buenas prácticas de construcción de imágenes Docker, según los requisitos del práctico.

---

# 1. Tamaño total de la imagen

El análisis realizado con **Dive** indica que la imagen tiene un tamaño final de:

**👉 126 MB**

Este tamaño es adecuado para una imagen basada en `python:3.10-slim`, combinada con dependencias instaladas vía `pip`.

---

# 2. Análisis de capas (Dive)

Las capas más relevantes detectadas por Dive fueron:

| Tamaño | Descripción |
|--------|-------------|
| **79 MB** | Capa base (`python:3.10-slim`) |
| **39 MB** | Instalación de paquetes del sistema con `apt-get` |
| **3.8 MB** | Actualización inicial y utilidades |
| **8.9 kB** | Creación de usuario no-root |
| **0 B** | Copia de archivos y configuración |

Dive también indica:

- **Potential wasted space:** 5.7 MB  
- **Image efficiency:** 96%

---

# 3. Buenas prácticas implementadas

## ✔ No ejecutar como root

La imagen incluye:

```
RUN useradd -m appuser
USER appuser
```

Por lo tanto, el proceso `python app.py` NO se ejecuta con permisos root.

---

## ✔ Uso de multi-stage builds

### Etapa Builder

```
FROM python:3.10-slim AS builder
pip install --user -r requirements.txt
```

### Etapa Final

```
FROM python:3.10-slim
COPY --from=builder /root/.local /root/.local
```

Esto garantiza que solo se copien al runtime final los paquetes estrictamente necesarios.

---

# 4. Análisis de vulnerabilidades (Trivy)

Se realizó un escaneo completo con **Trivy**, obteniendo los siguientes resultados:

---

## Vulnerabilidades del sistema operativo (Debian 13.2)

**Total: 52**

- 51 **LOW**
- 1 **MEDIUM**
- 0 **HIGH**
- 0 **CRITICAL**

Estas vulnerabilidades provienen del sistema base Debian Slim y son comunes en entornos reales.

---

## Vulnerabilidades en dependencias Python

**Total: 7**

- 6 **MEDIUM**
- 1 **HIGH**  
  · Vulnerabilidad asociada al paquete `Flask-Cors 4.0.0`  
  · Solucionada en la versión `4.0.2`

Esta vulnerabilidad puede mitigarse actualizando el paquete.

---

## Conclusión del análisis con Trivy

- No existen vulnerabilidades **CRITICAL** ni **HIGH** en el sistema operativo.  
- Las vulnerabilidades encontradas son de bajo riesgo y esperables.  
- El nivel de riesgo general de la imagen es **bajo**.  

---

# 5. Conclusión general

La imagen `app-notas:1.0`:

- No utiliza `latest`
- No ejecuta procesos como root
- Está optimizada mediante multi-stage builds
- Presenta **96% de eficiencia** (Dive)
- Tiene solo **5.7 MB de espacio desperdiciado**
- Fue auditada con **Trivy** y **Dive**
- No presenta vulnerabilidades críticas

En conclusión, la imagen es **segura, eficiente y cumple todos los requisitos del ejercicio**.

---
