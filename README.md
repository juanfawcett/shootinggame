# DOCUMENTACIÓN DEL PROCESO DE MANTENIMIENTO DEL VIDEOJUEGO SHOOTINGGAME

## 1. Introducción

Este documento describe el proceso de mantenimiento realizado sobre el videojuego ShootingGame, desarrollado inicialmente por un tercero y entregado al cliente. Tras un periodo de uso, el cliente reportó errores en el funcionamiento del juego y solicitó nuevas funcionalidades. Con el fin de mejorar el producto, se abrió una licitación a la cual se presentaron dos grupos conformados por estudiantes del Módulo de Mantenimiento de Software de la Especialización en Desarrollo de Software de la Universidad del Magdalena.
El presente informe consolida todas las actividades realizadas durante el mantenimiento, incluyendo la identificación de problemas, corrección de fallos, incorporación de mejoras, análisis técnico, uso de LLMs y argumentación basada en los conceptos del módulo. El proceso tuvo una duración de 7 días.

## 2. Objetivos

### 2.1. Objetivo general

Implementar el proceso de mantenimiento del videojuego ShootingGame, documentando todas las actividades realizadas durante la corrección de fallos y la incorporación de nuevas funcionalidades solicitadas por el cliente.

### 2.2. Objetivos específicos

- Realizar las correcciones del videojuego.
- Implementar las mejoras solicitadas por el usuario.
- Registrar detalladamente todas las actividades realizadas.

## 3. Descripción del sistema mantenido

### 3.1. Origen del software

El videojuego fue desarrollado por un programador independiente contratado por el cliente. Tras problemas percibidos en el gameplay y la necesidad de nuevas características, el cliente libera el proyecto mediante licitación académica.

### 3.2. Repositorio

Repositorio oficial entregado por el cliente:
https://github.com/lermretat/shootinggame
Se realiza fork con link https://github.com/juanfawcett/shootinggame, para manejo interno del equipo.

### 3.3. Tecnología

- Lenguaje principal: Python
- Motor/base: Panda3D
- Arquitectura: Monolítica estructurada (Migrada a Modular)
- Patrón principal: Loop de juego clásico

## 4. Organización del equipo

El equipo estará conformado por 2 desarrolladores, un arquitecto y un analista de calidad.
Se adopta la siguiente estructura común:

- Líder técnico y arquitecto: Ing. Juan Fawcett
- Responsable de pruebas: Ing. Rafael Bonnet
- Desarrollador #1: Ing. Fredy Caballero
- Desarrollador #2: Ing. Cristian Avila

## 5. Proceso de mantenimiento aplicado

El proceso se basó en el modelo clásico de mantenimiento sugerido por el estándar y los contenidos del módulo:

- Análisis del requerimiento o problema reportado
- Clasificación del tipo de mantenimiento
- Planificación de tareas por cada día
- Ejecución de mantenimiento (codificación)
- Pruebas y verificación
- Documentación del cambio
- Actualización del repositorio

## 6. Actividades realizadas por tipo de mantenimiento

### 6.1. Mantenimiento correctivo

#### Bug reportado 1:
“La nave tiene 3 puntos de vida; pero a veces con solo una explosión lo destruyen.”

**Análisis**
- El error es intermitente, lo cual sugiere un cálculo incorrecto de colisiones.
- Se revisó el código y se identificó que la función que detecta impacto registra múltiples colisiones en un solo frame.
- El daño se procesa varias veces si la nave permanece solapada con el sprite de explosión.

**Solución implementada**
- Se modificó la lógica de colisión para eliminar el nodo del enemigo inmediatamente tras el primer contacto.
- Se implementó el uso de `continue` en el bucle de actualización para evitar re-procesar el mismo objeto.

**Pruebas**
- Se realizaron pruebas de colisión y se verificó en gameplay que la nave recibe exactamente 1 daño por impacto.

#### Bug reportado 2: [BUG-0003] Duplicidad en el Score
**Análisis**
- Se detectó que el sistema realizaba una acumulación errónea en el historial de puntajes al perder la partida.
- La función de finalización (`endGame`) se ejecutaba múltiples veces consecutivas en el mismo frame debido a la falta de validación de estado.

**Solución implementada**
- Se agregó una **Cláusula de Guardia** al inicio del método `endGame`. Ahora verifica si `gameOver` es True; si lo es, detiene la ejecución inmediatamente.

**Conclusión**
Los errores quedaron corregidos. Se registraron como mantenimiento correctivo.

### 6.2. Mantenimiento perfectivo (nueva funcionalidad)

### Iniciativa propia
Refactorización ligera:
- Separación de archivos por tipo de responsabilidad (`game.py`, `ui.py`, `sprites.py`).

#### Solicitud del cliente:
“Guardar un histórico de los mejores tiempos.”

**Análisis**
El juego no posee persistencia. No existe un módulo para almacenar records.

**Solución implementada**
- [cite_start]Crear archivo `highscores.json` persistente[cite: 25].
- Modificar el sistema de fin de partida para:
    1. Calcular tiempo sobrevivido de forma **acumulativa** (sumando el tiempo de todas las etapas/stages superadas antes de morir).
    2. Guardar y ordenar los tiempos de mayor a menor.
    3. Mostrar en la interfaz (HUD) el **Top 3** de mejores tiempos.

**Cambios**
- Se integró la librería `json` y `os` en `game.py`.
- Se actualizó `ui.py` para renderizar la lista de puntajes dinámicamente.

**Pruebas**
- Insertar tiempos simulados, verificar orden descendente y persistencia al cerrar el juego.

### Iniciativa propia
El juego no cuenta con un menú de bienvenida antes de que el juego inicie.

### Iniciativa del cliente
"El juego no tiene diferentes niveles de dificultad, está muy difícil"

#### Selector de niveles
- Se añadió un selector inicial (Low, Medium, Advanced) antes de iniciar el juego.
- La selección aplica multiplicadores a: intervalo de disparo, intervalo de spawn de enemigos y velocidad de enemigos.

#### Acción
Se agrega un texto al inicio que indica al usuario que debe presionar enter para poder iniciar el juego.

### 6.3. Mantenimiento adaptativo

Se ajustó el videojuego para soportar cambios en versiones actuales del motor y Python.
Incluyó:
- Actualización de métodos de carga de imágenes.
- Ajustes en rutas relativas para compatibilidad de assets.
- Correcciones en configuraciones de pantalla y compatibilidad con Panda3D.

### 6.5. Mantenimiento preventivo

- Documentación de todas las funciones.
- Creación de archivo README.md ampliado.
- Eliminación de código repetido en los loops de enemigos.
- Mejor organización de assets en carpetas.

## 7. Técnicas de mantenimiento aplicadas

### 7.1. Reingeniería
- Se reconstruyó parcialmente el módulo de colisiones para hacerlo más mantenible.
- Se reestructuró la lógica de daño y la gestión de fin de juego (Game Over).

### 7.2. Refactorización
- Se reorganizó el código monolítico en módulos (`ui`, `sprites`, `game`) con funciones pequeñas y claras.
- Se eliminaron condicionales redundantes.

### 7.3. Ingeniería inversa
- Debido a la falta de documentación, se analizó el código legado para entender su funcionamiento.
- Se generó un diagrama de flujo básico del loop principal.

## 8. Uso de LLMs en el proceso

Durante el desarrollo se emplearon LLMs como asistentes para:
- Explicar secciones del código heredado.
- Proponer soluciones de refactorización.
- Detectar la causa raíz del bug de duplicidad de score (Race condition lógico).
- Acelerar la documentación.
- Detectar posibles fallos en la lógica.

Se deja constancia de que las decisiones finales y la implementación fueron realizadas por los integrantes del equipo.

## 9. Plan de trabajo

Se usa Trello para manejo de incidencias, Github como control de versiones, PR para aprobación de cambios y Gitflow para todo el flujo desde el desarrollo hasta el release.

## 10. Conclusiones

El proceso de mantenimiento aplicado permitió:
- Corregir el bug crítico que afectaba la vida del jugador y la duplicidad de puntajes.
- Implementar la nueva funcionalidad solicitada por el cliente (histórico de mejores tiempos Top 3 Acumulativo).
- Realizar casos representativos de los cuatro tipos de mantenimiento: correctivo, adaptativo, perfectivo y preventivo.
- Aplicar técnicas profesionales como reingeniería, refactorización e ingeniería inversa.
- Mantener una documentación detallada conforme a las rúbricas del módulo.
- El videojuego ahora es más estable, más funcional, más fácil de mantener y alineado con las expectativas del cliente.
