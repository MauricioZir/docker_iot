# FLASK

Utiliza una conexión a la base de datos para obtener el listado de nodos o brokers.
Desde la página se puede agregar o modificar los brokers.
La tabla que utiliza para almacenar esta información se puede crear con el script nodos.sql.

Para guardar la contraseña del broker en la base de datos, utiliza una libreria de cifrado
"Fernet" para poder recuperar la contraseña en el backend cuando se quiere realizar la conexión.

Para esto, se debe definir la variable de entorno FERNET_KEY, la cual debe ser una cadena codificada 
en Base64 URL-safe de exactamente 44 caracteres.
