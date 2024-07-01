# MSSCAE24 TP Final

## Instrucciones de ejecución

### Dependencias
Se requiere python 3.10 o superior

Se recomienda crear un virtualenv para evitar conflictos de dependencias: `sudo apt install python3.10-venv && python3 -m venv myvenv && source myvenv/bin/activate`

Luego, dentro del virtualenv, ejecutar `pip install -r requirements.txt` (alternativamente, se puede usar Poetry)

Finalmente, se puede abrir el notebook usando `jupyter lab`. En `notebooks/tp_final.ipynb` se encuentra el Jupyter notebook con todo el análisis.

## Ver resultados sin ejecutar
Alternativamente, debido al elevado tiempo de ejecución (aprox hora y media), adjuntamos el exportado `notebooks/tp_final.html`

## Estructura del proyecto
- `notebooks/`: Jupyter notebooks con el análisis (el ejecutable y el exportado)
- `scenarios/`: configuraciones iniciales de autómatas, usadas en los notebooks
- `src/`: modelado del problema
  - `market.py`: autómata celular que representa todo el mercado. Se encarga de la
  inicialización de los agentes, y de la de cada paso. Además, computa las variables
  macro en cada paso, para después graficarlas
  - `producer.py` y `consumer.py`: agentes de productor y consumidor, respectivamente
  - `profit_period.py`: se encarga de computar ganancias y decidir las variaciones de
    precio en cada paso (cada Producer tiene una instancia de ProfitFormula)
  - `bankrupted_utils.py`: funciones que se usan en el notebook, para la parte de
  bancarrota

