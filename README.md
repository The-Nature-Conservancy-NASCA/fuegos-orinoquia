# fuegos-orinoquia
Este repositorio contiene el código fuente para el análisis de dinámicas espacio-temporales de incendios en la Orinoquía colombiana y su relación con tres variables diferentes: (1) accesibilidad humana, (2) cobertura de la tierra y (3) acumulación y disponibilidad de biomasa.

## Cómo reproducir

### Requisitos
El código fuente requiere la instalación de Python y diferentes librerías de computación científica. Con el fin de facilitar esta instalación y evitar conflictos con otras posibles instalaciones de Python en su sistema, se recomienda utilizar `conda`, un gestor de entornos y paquetes. Puede descargar instalar [Anaconda](https://www.anaconda.com/products/individual) o [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (una versión ligera).

Adicionalmente, se recomienda tener una máquina con mínimo 16 GB de memoria RAM puesto que varias operaciones implican el uso de cubos de datos y son computacionalmente intensas.

### Entorno virtual
Una vez instalado `conda`, descargue o clone este repositorio en su máquina. Ubíquese en la raíz del proyecto y ejecute el siguiente comando para instalar un entorno virtual con las librerías necesarias:

```shell
conda create env -f environment.yml
```

### Activación entorno virtual
Para poder ejecutar los scripts es necesario activar el entorno virtual recién instalado. Para esto ejecute:

```shell
conda activate fuegos-orinoquia
```

### Ejecución
Los scripts se deben correr en el orden en el que se encuentran dentro de la carpeta [`src`](src) y sus respectivas sub-carpetas (sin tener en cuenta la carpeta `utils` que corresponde a utilidades usadas por múltiples scripts en el proyecto). Para ejecutar un script debe asegurarse que el directorio activo de trabajo sea igual a la ubicación de este y luego debe ejecutar `python` y pasar el nombre del script como primer argumento. Por ejemplo, para ejecutar el primer script (estando ubicado desde la raíz del proyecto):

```shell
cd src/01_download
python 01_submit_appeears_task.py
```

Una vez ejecutados todos los scripts, se crearán tres nuevas carpetas en la raíz del proyecto:

* `data`: contiene los datos descargados y transformados para cada región.
* `figures`: contiene figuras resultantes del análisis.
* `results`: contiene tablas en formato `csv` y `xlsx` con los resultados del análisis.

## Consideraciones
* Los scripts descargan el producto de área quemada de MODIS (MCD64A1) utilizando [AppEEARS API](https://lpdaacsvc.cr.usgs.gov/appeears/api/). El uso de esta herramienta necesita una cuenta en [`Earth Data`](https://urs.earthdata.nasa.gov/). Regístrese y reemplace las líneas correspondientes con sus credenciales en el archivo [`constants.py`](src/utils/constants.py).
* Otros datos de entrada (*i.e.* cobertura de la tierra, precipitación y polígonos de las regiones) deben ser descargados manualmente antes de ejecutar los scripts. Estos archivos se encuentran en: https://tnc.box.com/s/492eqegz1b40z1yxjr8y7suqfy1l8yka.
