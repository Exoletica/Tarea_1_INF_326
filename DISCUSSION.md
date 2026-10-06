# Discusión sobre Trade-offs y 

## Trade-offs Detectados

### El primer trade-off detectado está en usar publish-subscribe con RabbitMQ.

**La ventaja es el desacoplamiento.** El publisher no necesita conocer a los cinco subscribers ni llamarlos directamente. Publica una vez y RabbitMQ se encarga de distribuir el evento. Como consecuencia de esto, es que el agregar más subscribers sea relativamente sencillo. 

Sin embargo, **el costo o desventaja es que se agrega un componente adicional, RabbitMQ**, que debe instalarse, configurarse y mantenerse. Si RabbitMQ falla o no está disponible, la comunicación entre publisher y subscribers se interrumpe. Este costo es aceptable actualmente debido al bajo número de componentes y de eventos esperado.

Para este dominio, este trade-off **sí es de consideración**, ya que la disponibilidad del sistema de mensajería es relevante para que las notificaciones lleguen a los subscribers. Sin embargo, dado el alcance acotado de la tarea y la pequeña cantidad de componentes, el costo de mantener RabbitMQ es aceptable.


### El segundo trade-off está en usar un exchange fanout.

**La ventaja es muy clara: todos los subscribers reciben el evento** y cada uno decide si está interesado. Eso encaja perfectamente con el requisito de que cada subscriber determine si el sismo está a menos de 500 km. 

**La desventaja es que se envía el mensaje a todos** aunque la mayoría no esté interesada. Con solo cinco subscribers esto casi no importa, **pero si hubiera miles de subscribers** distribuidos por todo el país o el mundo, estaríamos generando tráfico y procesamiento innecesario. 

En el dominio, este trade-off no es especialmente crítico, ya que solo existen cinco subscribers y los mensajes contienen muy poca información. No obstante, podría transformarse en un problema de escalabilidad si el número de subscribers creciera considerablemente.

### El último trade-off  se encuentra en la existencia de un mensaje mínimo. 

Se decidió solo enviar:

``` json
{
  "id": "sismo-001",
  "latitud": -33.036,
  "longitud": -71.629
}
```


**La ventaja es que los mensajes son pequeños** y contienen solo lo necesario para decidir si el evento es relevante. 

Pero **la desventaja es que un subscriber interesado necesita hacer una segunda operación**, es decir, consultar el servicio HTTP. Entonces se cambió “mensajes más grandes” por “más solicitudes HTTP”. Si se enviaran toda la información en RabbitMQ, no necesitaríamos ese GET, pero estaríamos enviando magnitud, profundidad, escala, referencia y otros campos incluso a subscribers que no los necesitan. 

En el dominio presentado, este trade-off tampoco parece crítico, porque solo los subscribers interesados realizan la consulta HTTP. Con cinco subscribers, la cantidad de solicitudes adicionales es pequeña. Sin embargo, si muchos subscribers estuvieran interesados simultáneamente, el servicio HTTP podría convertirse en un cuello de botella.

## Back of the Envelope

Para estimar el uso del sistema se podría realizar una aproximación a partir de la frecuencia de ocurrencia de sismos, la cantidad de subscribers y el tamaño de los mensajes.

Primero, la **cantidad de entregas de mensajes** en RabbitMQ sería aproximadamente:

$Entregas = Cantidad\ de\ sismos × Cantidad\ de\ subscribers$

Esta cantidad se debe a que se implementó un exchange fanout, donde se notifica a todos los subscribers de la ocurrencia de un sismo. Actualmente solo existen cinco subscribers, por lo que cada evento de sismo genera cinco entregas de mensajes. 

Luego, se podría estimar la **cantidad de consultas realizadas al servicio HTTP**. Esta cantidad dependería de cuántos subscribers se encuentren a menos de 500 km del sismo:

$Consultas\ HTTP = Cantidad\ de\ sismos × Promedio\ de\ subscribers\ interesados\ por\ sismo$

Este valor sería menor o igual a la cantidad total de entregas de mensajes, ya que solo los subscribers interesados realizan una petición HTTP.

Por otro lado, se podría estimar el **tráfico generado por RabbitMQ** a partir del tamaño promedio del mensaje:

$Tráfico\ de\ mensajería = Cantidad\ de\ entregas × Tamaño\ promedio\ del\ mensaje$

Como el evento publicado contiene únicamente un identificador, latitud y longitud, el tamaño del mensaje es reducido.

Estas estimaciones permitirían evaluar si la arquitectura actual es suficiente para la carga esperada. Con solo cinco subscribers y mensajes pequeños, el costo de distribuir cada evento a todos los componentes es bajo. Sin embargo, si el sistema creciera en cantidad de subscribers, la cantidad de entregas en RabbitMQ y las consultas HTTP podrían aumentar considerablemente, por lo que podría ser necesario reconsiderar la estrategia de distribución o escalar los componentes.

