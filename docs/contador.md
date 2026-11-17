# Contador de visitas — preparado y DESACTIVADO

Estado: `counter.js` tiene `enabled:false`. Con eso no se envía nada a nadie y la nota de privacidad dice «sin contador de visitas».

## Qué hace si se activa
- Solo suma visitas, por sección (`/`, `/2d/`, `/proyecto/`). Es un píxel de 1×1 hacia GoatCounter, sin el script de terceros.
- Nunca envía el nombre buscado (`?q=`), la ficha abierta (`#s=`, `#p=`), el título ni la página de procedencia (`no-referrer`).
- Sin cookies ni localStorage. Si el navegador pide «no rastrear» (DNT o GPC), no cuenta. Tampoco cuenta en local ni con navegadores automáticos.
- GoatCounter (https://www.goatcounter.com/help/privacy, consultado el 17-11-2026): no guarda la IP ni el User-Agent completo, solo totales. Sus servidores están en Hetzner (Alemania y Finlandia) y lo opera Martin Tournoij (Irlanda). Es gratis para un uso público razonable. Su autor cree que no hace falta aviso de consentimiento (https://www.goatcounter.com/help/gdpr), pero aclara que no es abogado. Nosotros tampoco.

## Lo que tiene que hacer Carlos (una sola vez)
1. Crear una cuenta gratuita en https://www.goatcounter.com/signup con su correo y una contraseña. Esa contraseña no se escribe nunca en el chat.
2. Elegir un código, por ejemplo `lista-kauffmann`. El panel quedará en `https://lista-kauffmann.goatcounter.com`.
3. En *Settings*, desactivar todo lo que no haga falta para contar: navegador, sistema, idioma, tamaño de pantalla y ubicación. Así solo quedan los totales.
4. Pasarme solo el código, no la contraseña.

## Lo que hago yo después, y solo con su OK
- En `counter.js`, poner `enabled: true, endpoint: 'https://CODIGO.goatcounter.com/count'`.
- En `LICENCIAS.md`, cambiar la línea 3: «sin analítica» pasa a «con un contador de visitas anónimo (GoatCounter), sin cookies».
- Pasar las pruebas (`tests/run-all.sh`), comprobar en el sitio local que la nota «Privacidad» cambia sola al texto con GoatCounter, y publicar solo si él lo aprueba.
- Verificar en su panel que llega la primera visita. Que el píxel cuente sin cabecera Referer no se ha podido probar sin cuenta.

## Alternativas descartadas
- Cloudflare Web Analytics: también es gratis y sin cookies, pero necesita una cuenta de Cloudflare (empresa de EE. UU.) y cargar su script desde static.cloudflareinsights.com.
- Contador propio (GoatCounter, Umami o Plausible autoalojados): hace falta un servidor propio que mantener y pagar. GitHub Pages no lo permite.
- GitHub «Traffic»: solo lo ve el dueño del repositorio y cuenta las visitas al repositorio, no a la web publicada.
