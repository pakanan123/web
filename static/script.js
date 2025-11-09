// static/script.js
document.addEventListener('DOMContentLoaded', () => {
  // Tool: converter
  const convertBtn = document.getElementById('convert-btn');
  if (convertBtn) {
    const input = document.getElementById('dec-input');
    const result = document.getElementById('convert-result');
    const clearBtn = document.getElementById('clear-btn');
    convertBtn.addEventListener('click', () => {
      const v = parseInt(input.value);
      if (isNaN(v)) {
        result.textContent = 'กรุณากรอกตัวเลขที่ถูกต้อง';
        return;
      }
      result.textContent = `Binary: ${v.toString(2)}  —  Hex: ${v.toString(16).toUpperCase()}`;
    });
    if (clearBtn) clearBtn.addEventListener('click', () => {
      input.value=''; result.textContent='';
    });
  }

  // Quiz: load random question + submit
  const loadBtn = document.getElementById('load-btn');
  const nextBtn = document.getElementById('next-btn');
  const qText = document.getElementById('q-text');
  const choicesDiv = document.getElementById('choices');
  const feedback = document.getElementById('feedback');

  async function loadQuestion(){
    feedback.textContent = '';
    qText.textContent = 'กำลังโหลด...';
    choicesDiv.innerHTML = '';
    try {
      const res = await fetch('/api/random_question');
      if (!res.ok) throw new Error('ไม่มีคำถาม');
      const data = await res.json();
      // attach
      qText.textContent = data.question;
      data.choices.forEach(choice => {
        const b = document.createElement('button');
        b.className = 'btn';
        b.textContent = choice;
        b.addEventListener('click', async () => {
          // submit
          const payload = { question_id: data.id, selected: choice };
          const r2 = await fetch('/api/submit_answer', {
            method:'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify(payload)
          });
          const resjson = await r2.json();
          if (resjson.correct) {
            feedback.textContent = 'ถูกต้อง! 🎉';
            feedback.style.color = 'green';
          } else {
            feedback.textContent = `ผิด! คำตอบที่ถูกคือ: ${resjson.correct_answer}`;
            feedback.style.color = 'red';
          }
        });
        choicesDiv.appendChild(b);
      });
    } catch(err){
      qText.textContent = 'ไม่สามารถโหลดคำถามได้';
      console.error(err);
    }
  }

  if (loadBtn) {
    loadBtn.addEventListener('click', loadQuestion);
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', loadQuestion);
  }
});
