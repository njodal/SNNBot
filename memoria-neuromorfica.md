# Memoria Neuromórfica

## Nivel 1: Retina
- 3 sensores de movimiento, cada uno dispara un pulso al detectar cambio en su punto.
- 2 sensores adicionales: uno para movimiento a la izquierda, otro para la derecha.

## Nivel 2: Capa AND (patrones)
- Neuronas conectadas al azar con todos los sensores.
- Aprendizaje por poda hebbiana: las sinapsis que coinciden en el tiempo se fortalecen; las que no coinciden desaparecen.
- Ejemplo: una neurona reconoce que los sensores 1 y 3 se prenden juntos; otra reconoce 2 y 3.

## Nivel 3: Capa de secuencia temporal
- Se conecta a las salidas AND ya estabilizadas (no arranca densa).
- Cada neurona aprende el orden: patrón A precede a patrón B dentro de una ventana de tiempo.
- También recibe los sensores de dirección (izquierda/derecha) para registrar la causa de cada transición.
- Cada arista del grafo tiene dos etiquetas: orden temporal y causa del movimiento.

## Nivel 4: Recuerdo (salida)
- Una neurona final que codifica la cadena completa: secuencia de patrones + causa de cada transición.
- Memoria episódica: no solo qué pasó, sino por qué pasó.
