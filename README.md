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
- Motor/base: Pygame (Panda3d)
- Arquitectura: Monolítica estructurada
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
- jecución de mantenimiento (codificación)
- Pruebas y verificación
- Documentación del cambio
- Actualización del repositorio

## 6. Actividades realizadas por tipo de mantenimiento

### 6.1. Mantenimiento correctivo

#### Bug reportado:

“La nave tiene 3 puntos de vida; pero a veces con solo una explosión lo destruyen.”
Análisis

- El error es intermitente, lo cual sugiere un cálculo incorrecto de colisiones.
- Se revisó el código.
- Se identificó que la función que detecta impacto registra múltiples colisiones en un solo frame.
- El daño se procesa varias veces si la nave permanece solapada con el sprite de explosión.

#### Solución implementada

- Se añadió un estado de invulnerabilidad breve (cooldown de impacto).
- Se normalizó el cálculo para que solo se procese un evento de daño por explosión.
  Pruebas
- Se realizaron pruebas de colisión.
- Se probó en gameplay que la nave recibe exactamente 1 daño por explosión.

#### Conclusión

El error quedó corregido. Se registró como mantenimiento correctivo.

### 6.2. Mantenimiento perfectivo (nueva funcionalidad)

### Iniciativa propia

Refactorización ligera:

- Separación de archivos por tipo de responsabilidad.

#### Solicitud del cliente:

“Guardar un histórico de los mejores tiempos.”

#### Análisis

El juego no posee persistencia. No existe un módulo para almacenar records.
Solución implementada

- Crear archivo highscores.json persistente.
- Modificar el sistema de fin de partida para:

1. Calcular tiempo sobrevivido.
2. Guardarlo si está dentro del top 5.
3. Mostrar un menú de records.
   Cambios
   • Se creó un nuevo módulo score_manager.py.
   • Se agregó un menú opcional en la pantalla inicial.
   Pruebas
   • Insertar tiempos simulados.
   • Verificar orden descendente.
   • Verificar persistencia entre ejecuciones.

### 6.3. Mantenimiento adaptativo

Se ajustó el videojuego para soportar cambios en versiones actuales de Pygame (ej: warnings y sintaxis).
Incluyó:

- Actualización de métodos de carga de imágenes.
- Ajustes en rutas relativas.
- Correcciones en configuraciones de pantalla.

### 6.5. Mantenimiento preventivo

- Documentación de todas las funciones.
- Creación de archivo README.md ampliado.
- Eliminación de código repetido en los loops de enemigos.
- Mejor organización de assets.

## 7. Técnicas de mantenimiento aplicadas

### 7.1. Reingeniería

- Se reconstruyó parcialmente el módulo de colisiones para hacerlo más mantenible.
- Se reestructuró la lógica de daño.

### 7.2. Refactorización

- Se reorganizó el código en funciones pequeñas y claras.
- Se eliminaron condicionales redundantes.

### 7.3. Ingeniería inversa

- Debido a la falta de documentación, se analizó el código para entender su funcionamiento.
- Se generó un diagrama de flujo básico del loop principal.

## 8. Uso de LLMs en el proceso

Durante el desarrollo se emplearon LLMs como ChatGPT para:

- Explicar secciones del código heredado.
- Proponer soluciones de refactorización.
- Sugerir patrones de diseño aplicables.
- Acelerar la documentación.
- Detectar posibles fallos en la lógica.
  Se deja constancia de que las decisiones finales fueron tomadas por los integrantes del equipo, no por el LLM.

## 9. Plan de trabajo

Se usa Trello para manejo de incidencias, Github como control de versiones, PR para aprobación de cambios y Gitflow para todo el flujo desde el desarrollo hasta el reléase.

## 10. Conclusiones

El proceso de mantenimiento aplicado permitió:

- Corregir el bug crítico que afectaba la vida del jugador.
- Implementar la nueva funcionalidad solicitada por el cliente (histórico de mejores tiempos).
- Realizar casos representativos de los cuatro tipos de mantenimiento: correctivo, adaptativo, perfectivo y preventivo.
- Aplicar técnicas profesionales como reingeniería, refactorización e ingeniería inversa.
- Mantener una documentación detallada conforme a las rúbricas del módulo.
- El videojuego ahora es más estable, más funcional, más fácil de mantener y alineado con las expectativas del cliente.

## 11. Cambios ejecutados Niveles de dificultad

Se documentan los cambios implementados durante el mantenimiento:

1. Selector de niveles
   - Se añadió un selector inicial (Low, Medium, Advanced) antes de iniciar el juego.
   - La selección aplica multiplicadores a: intervalo de disparo, intervalo de spawn de enemigos y velocidad de enemigos.

2. Eliminación de números mágicos
   - Todas las constantes de juego, posiciones y parámetros visuales fueron extraídas a `game_config.py`.
   - Nuevas constantes: parámetros del selector de niveles, márgenes off-screen, tolerancias de colisión, escalas y rutas de assets.

3. Configuración por dificultad
   - Se añadió `DIFFICULTY_SETTINGS` en `game_config.py` con los multiplicadores para `low`, `medium` y `advanced`.
   - `ShootingGame` usa esos valores para ajustar `currentShotInterval`, `enemy_spawn_interval` y velocidad de enemigos.

4. Gestión de tareas y reinicio
   - Las tareas principales (`updateTask`, `autoShootTask`, `spawnEnemyTask`, `spawnBonusTask`) se inician solo después de seleccionar nivel.
   - `restartGame` respeta la dificultad seleccionada y restablece intervalos y tareas correctamente.

5. Bonificaciones y disparo automático
   - `applyBonusEffect` recalcula el intervalo y la escala de disparo en tiempo real y reinicia la tarea de auto disparo.
   - Los bonuses usan posiciones definidas en la configuración y cambian textura según su valor.

6. Corrección de colisiones (mantenimiento correctivo)
   - Se corrigió el procesamiento múltiple de daño por colisión para evitar decrementos excesivos de vida.
   - Se añadió un breve periodo de invulnerabilidad tras recibir daño (cooldown) y se normalizó la lógica de detección.

7. Persistencia de records (mejora perfectiva)
   - Implementación de `highscores.json` y módulo `score_manager.py` para mantener top 5 de mejores tiempos.
   - Menú opcional para mostrar records en la pantalla inicial.

8. Refactor y adaptaciones
   - Reorganización del código en funciones y módulos (separación de configuración, manejo de scores).
   - Ajustes de compatibilidad con versiones actuales de Panda3D/Pygame y rutas de assets.

9. Beneficios
   - Facilita tuning y pruebas al centralizar parámetros.
   - Permite cambiar dificultad sin tocar código.
   - Mejora la estabilidad y mantenibilidad del juego.

(Ver los archivos modificados y los commits para detalles técnicos y pruebas realizadas.)