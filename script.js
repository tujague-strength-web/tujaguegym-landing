/* ==========================================================================
   TujagueGYM — captura de leads
   --------------------------------------------------------------------------
   Configurá ENDPOINT con la URL de tu servicio de formularios (Formspree,
   Getform, Google Apps Script, tu propia API...). Mientras esté vacío, la
   página funciona en "modo demo": valida, simula el envío y guarda los datos
   en localStorage para que puedas probarla sin backend.
   ========================================================================== */

const CONFIG = {
  ENDPOINT: '',                            // ej: 'https://formspree.io/f/xxxxxxx'
  PDF_URL: 'rutina-4-semanas.pdf',         // ruta o URL del PDF de la rutina
};

const form       = document.getElementById('lead-form');
const submitBtn  = document.getElementById('submit-btn');
const statusEl   = form.querySelector('.form-status');
const successEl  = document.getElementById('success');

document.getElementById('year').textContent = new Date().getFullYear();
document.getElementById('download-link').href = CONFIG.PDF_URL;

/* ------------------------------------------------------------- Validación */

const validators = {
  nombre: (v) => {
    if (!v.trim()) return 'Ingresá tu nombre.';
    if (v.trim().length < 2) return 'El nombre es demasiado corto.';
    return '';
  },
  email: (v) => {
    if (!v.trim()) return 'Ingresá tu email.';
    if (!/^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(v.trim())) return 'Revisá el formato del email.';
    return '';
  },
  whatsapp: (v) => {
    if (!v.trim()) return '';                        // campo opcional
    const digits = v.replace(/\D/g, '');
    if (digits.length < 8) return 'Ingresá un número válido o dejalo vacío.';
    return '';
  },
  objetivo: (v) => (v ? '' : 'Elegí tu objetivo.'),
};

function showError(field, message) {
  const input = form.elements[field];
  const errorEl = form.querySelector(`[data-error-for="${field}"]`);

  if (message) {
    input.setAttribute('aria-invalid', 'true');
    errorEl.textContent = message;
    errorEl.hidden = false;
  } else {
    input.removeAttribute('aria-invalid');
    errorEl.hidden = true;
  }
}

function validateField(field) {
  const message = validators[field](form.elements[field].value);
  showError(field, message);
  return !message;
}

// Revalida en vivo una vez que el campo ya mostró un error.
Object.keys(validators).forEach((field) => {
  const input = form.elements[field];
  input.addEventListener('blur', () => validateField(field));
  input.addEventListener('input', () => {
    if (input.getAttribute('aria-invalid') === 'true') validateField(field);
  });
  input.addEventListener('change', () => {
    if (input.getAttribute('aria-invalid') === 'true') validateField(field);
  });
});

/* ------------------------------------------------------------- Envío */

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.classList.toggle('is-loading', isLoading);
  submitBtn.querySelector('.btn-label').textContent =
    isLoading ? 'Enviando...' : 'Descargar rutina gratis';
}

function setStatus(message) {
  statusEl.textContent = message || '';
  statusEl.hidden = !message;
}

async function sendLead(lead) {
  if (!CONFIG.ENDPOINT) {
    // Modo demo: sin backend configurado.
    const saved = JSON.parse(localStorage.getItem('tujaguegym_leads') || '[]');
    saved.push(lead);
    localStorage.setItem('tujaguegym_leads', JSON.stringify(saved));
    await new Promise((resolve) => setTimeout(resolve, 700));
    console.info('[TujagueGYM] Modo demo — lead guardado localmente:', lead);
    return;
  }

  const response = await fetch(CONFIG.ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(lead),
  });

  if (!response.ok) throw new Error(`HTTP ${response.status}`);
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  setStatus('');

  const fields = Object.keys(validators);
  const isValid = fields.map(validateField).every(Boolean);

  if (!isValid) {
    form.querySelector('[aria-invalid="true"]').focus();
    return;
  }

  const lead = {
    nombre: form.elements.nombre.value.trim(),
    email: form.elements.email.value.trim(),
    whatsapp: form.elements.whatsapp.value.trim(),
    objetivo: form.elements.objetivo.value,
    origen: 'landing-rutina-4-semanas',
    fecha: new Date().toISOString(),
  };

  setLoading(true);

  try {
    await sendLead(lead);

    document.getElementById('success-name').textContent = lead.nombre.split(' ')[0];
    form.hidden = true;
    successEl.hidden = false;
    successEl.querySelector('h3').setAttribute('tabindex', '-1');
    successEl.querySelector('h3').focus();
  } catch (error) {
    console.error('[TujagueGYM] Error al enviar el lead:', error);
    setStatus('No pudimos enviar tus datos. Probá de nuevo en unos segundos.');
  } finally {
    setLoading(false);
  }
});
