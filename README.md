# TujagueGYM — Landing page

Landing de una sola página cuyo único objetivo es captar datos a cambio de una
rutina de musculación gratuita de 4 semanas.

## Archivos

| Archivo                    | Qué hace                                                     |
|----------------------------|--------------------------------------------------------------|
| `index.html`               | Estructura y textos de la página.                            |
| `styles.css`               | Estilos (paleta, tipografía, responsive).                    |
| `script.js`                | Validación del formulario, envío del lead y estado de éxito. |
| `rutina-4-semanas.pdf`     | El material que se descarga (9 páginas).                     |
| `tools/generar-rutina.py`  | Regenera ese PDF. `python3 tools/generar-rutina.py`          |
| `tools/pdf.py`             | Generador de PDF mínimo, en Python puro, sin dependencias.   |

Sin dependencias ni build: se abre directo en el navegador o se sube tal cual a
GitHub Pages, Netlify, Vercel o cualquier hosting.

## Pendiente: conectar el formulario

Hoy la página corre en **modo demo**: valida los datos, muestra el mensaje de
éxito y entrega el PDF, pero los datos quedan guardados sólo en el navegador de
cada visitante (`localStorage`). **Vos no recibís nada.**

Para empezar a recibir los leads, creá una cuenta gratuita en
[Formspree](https://formspree.io) (o [Getform](https://getform.io),
[Basin](https://usebasin.com)) y pegá la URL de tu formulario en `script.js`:

```js
const CONFIG = {
  ENDPOINT: 'https://formspree.io/f/TU_ID',   // <- pegar acá
  PDF_URL: 'rutina-4-semanas.pdf',
};
```

Con eso, cada envío te llega por email y queda registrado en el panel del
servicio. No hay que tocar nada más.

Si usás Mailchimp, Brevo o MailerLite, además podés configurar un email de
bienvenida automático que entregue el PDF.

## Editar la rutina

El contenido del PDF (ejercicios, series, textos) está en
`tools/generar-rutina.py`, en las listas `PLAN_A`, `PLAN_B` y `TECNICA`.
Después de editarlas:

```bash
python3 tools/generar-rutina.py
```

## Personalización rápida

- **Color de marca**: variable `--accent` en `styles.css`.
- **Fondo / textos**: variables `--bg`, `--text`, `--text-muted`.
- **Campos del formulario**: agregá el `<input>` en `index.html` y su regla en
  el objeto `validators` de `script.js`; el resto se maneja solo.

## Publicar cambios

El sitio está en GitHub Pages: cada `git push` a `main` lo actualiza solo (tarda
un minuto en verse).

```bash
git add -A
git commit -m "Actualizo textos"
git push
```
