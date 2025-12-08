document.addEventListener('DOMContentLoaded', () => {
  // auto-dismiss alerts
  document.querySelectorAll('.alert').forEach(a => setTimeout(()=> {
    a.style.transition = "opacity .4s";
    a.style.opacity = 0;
    setTimeout(()=> a.remove(), 420);
  }, 3500));

  // confirm-delete forms
  document.querySelectorAll('form.confirm-delete').forEach(f => {
    f.addEventListener('submit', e => {
      if (!confirm('Are you sure you want to delete this event? This action cannot be undone.')) e.preventDefault();
    });
  });
});


function sendMail(ev) {
  ev.preventDefault();
  const form = ev.target;
  const name = encodeURIComponent(form.name.value || '');
  const email = encodeURIComponent(form.email.value || '');
  const msg = encodeURIComponent(form.message.value || '');
  const subject = encodeURIComponent(`Contact from portfolio: ${name}`);
  const body = encodeURIComponent(`From: ${name} <${email}>\n\n${decodeURIComponent(msg)}`);

  // open default mail client
  window.location.href = `mailto:ngnguy26@colby.edu?subject=${subject}&body=${body}`;
  return false;
}


function sendEmail() {
  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const message = document.getElementById("message").value;

  const subject = "Message From Mulevents User";

  const body = encodeURIComponent(
    `Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`
  );

  const mailto = `mailto:ngnguy26@colby.edu?subject=${encodeURIComponent(subject)}&body=${body}`;

  window.location.href = mailto;
}

