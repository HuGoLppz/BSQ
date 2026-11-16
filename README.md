# BSQ

Proyecto final de la C Piscine: encontrar y dibujar el **cuadrado más grande** posible en un mapa, evitando los obstáculos.

```
9.ox                              .....xxxxxxx...............
...........................       ....oxxxxxxx...............
....o......................       .....xxxxxxxo..............
............o..............   →   .....xxxxxxx...............
...........................       ....oxxxxxxx...............
....o......................       .....xxxxxxx...o...........
...............o...........       .....xxxxxxx...............
...........................       ......o..............o.....
......o..............o.....       ..o.......o................
..o.......o................
```

## Explicación completa

En [`docs/index.html`](docs/index.html) hay una página que explica, en orden, **cómo se compila** el proyecto (Makefile, preprocesado, compilación, ensamblado y enlazado) y **cómo funciona** cada función del código. Descárgala y ábrela en el navegador. Incluye:

- **Seguimiento de variables:** 10 trazas reales de 6 funciones (`main`, `read_all`, `parse_number`, `validate_map`, `process_row` y `fill_square`). En cada una se avanza línea a línea y se ve el valor de cada variable, su historial y una explicación de qué hace la línea con esos valores. Se generan ejecutando el binario bajo `gdb`.
- **Demo interactiva** del algoritmo de programación dinámica.

La página se genera con los scripts de [`docs/build/`](docs/build) (en Linux, con `cc` y `gdb`):

```sh
python3 docs/build/make_traces.py   # ejecuta bsq bajo gdb → docs/build/traces.json
python3 docs/build/build_page.py    # template.html + código real + trazas → docs/index.html
```

## Estructura

```
ex00/
├── Makefile
├── includes/bsq.h
└── srcs/
    ├── main.c         # argumentos, archivos, stdin y salida
    ├── read_input.c   # lectura completa con buffer que se duplica
    ├── parse.c        # primera línea: número de filas y caracteres
    ├── validate.c     # validación del mapa
    └── solve.c        # programación dinámica + pintado del cuadrado
tests/
├── run_tests.sh       # batería de pruebas (Linux)
├── reference.py       # solucionador de referencia por fuerza bruta
├── gen_map.pl         # generador de mapas del enunciado
└── maps/              # mapas válidos e inválidos
docs/
├── index.html         # página explicativa (generada)
└── build/             # plantilla, trazador gdb y generador de la página
```

## Algoritmo

Programación dinámica: `dp = 1 + min(arriba, izquierda, diagonal)` para cada celda vacía y `0` para cada obstáculo.

- **Tiempo:** O(filas × columnas). Cada celda se visita una sola vez.
- **Memoria extra:** una sola fila de `cols + 1` enteros.
- **Salida:** el cuadrado se pinta directamente sobre el buffer leído y se imprime con un único `write`.

## Uso

```sh
cd ex00
make
./bsq mapa                 # uno o varios archivos
./bsq < mapa               # entrada estándar
cat mapa | ./bsq
perl ../tests/gen_map.pl 40 20 2 > mapa
bash ../tests/run_tests.sh # 44 pruebas: salida, errores, stdin, aleatorios, valgrind
```

## Normas seguidas

- Norma de 42: norminette da OK en todos los archivos.
- Sin bucles `for`.
- Funciones de 25 líneas como máximo.
- Variables declaradas sin inicializar.
- Llaves en su propia línea.
- Solo se usan `open`, `close`, `read`, `write`, `malloc` y `free`.
- Se compila con `cc -Wall -Wextra -Werror`.
