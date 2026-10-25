# Homebox

Inventario doméstico autoalojado ([sysadminsmedia/homebox](https://github.com/sysadminsmedia/homebox)):
ubicaciones anidadas (trastero › estantería › piso › caja), fotos, búsqueda y etiquetas QR.

## Acceso

Puerto `7745` del host, pensado para ir detrás de un proxy inverso con TLS (red local / VPN).
No publicarlo directamente en Internet.

- El proxy debe admitir subidas de al menos 10 MB (fotos del móvil). En nginx el límite
  por defecto es 1 MB: `client_max_body_size 10m;`.
- Si el proxy corre en el mismo HA (otro addon), puede llegar al addon por la red interna
  y el puerto del host se puede desactivar en *Red*: así nadie se salta el proxy.

## Configuración

| Opción | Descripción |
|--------|-------------|
| `hostname` | URL pública del proxy (p. ej. `https://inventario.midominio.com`). Se usa en los enlaces de los QR. Sin valor = se deduce de la petición. |
| `allow_registration` | Permite crear cuentas desde la pantalla de login. Dejar en `true` hasta crear los usuarios y pasar a `false`. |
| `trust_proxy` | Confía en las cabeceras `X-Forwarded-*`: IP real del cliente para el límite de intentos de login. Con el puerto 7745 accesible sin pasar por el proxy, un cliente puede falsear su IP y saltarse ese límite. |

## Datos y copias

Base de datos SQLite, fotos y el secreto `api_key_pepper` (generado en el primer arranque)
en `/data`: persisten entre reinicios y actualizaciones. El backup del addon es en frío
(`backup: cold`): se para unos segundos para que la copia de SQLite sea consistente.

## Actualizar Homebox

Dependabot abre un PR semanal si hay versión nueva (etiqueta + digest del `FROM`) y el
workflow `homebox-version` sube `version` y el `CHANGELOG.md` en el mismo PR. Al fusionarlo,
el builder publica la imagen y HA ofrece la actualización.

Cambios solo del addon (sin subir Homebox): `version` = etiqueta + `.N` (p. ej. `0.27.1.1`).
