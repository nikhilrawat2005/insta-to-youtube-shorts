// script.js

// Timer functionality
const timerEl = document.getElementById("timer");
if (timerEl && timerEl.dataset.time) {
  const start = new Date(timerEl.dataset.time.replace(" ", "T"));
  
  function updateTimer() {
    const now = new Date();
    let d = Math.floor((now - start) / 1000);
    let h = Math.floor(d / 3600);
    d %= 3600;
    let m = Math.floor(d / 60);
    let s = d % 60;
    
    // Format with leading zeros
    const hStr = h.toString().padStart(2, '0');
    const mStr = m.toString().padStart(2, '0');
    const sStr = s.toString().padStart(2, '0');
    
    timerEl.querySelector('.timer-digits').textContent = `${hStr}:${mStr}:${sStr}`;
  }
  
  // Update immediately and then every second
  updateTimer();
  setInterval(updateTimer, 1000);
}

// Drag and drop functionality
const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const browseBtn = document.getElementById('browse-btn');
const storeForm = document.getElementById('store-form');

if (dropArea && fileInput) {
  // Highlight drop area when dragging over
  ['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropArea.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropArea.classList.remove('dragover');
    });
  });

  // Handle dropped files
  dropArea.addEventListener('drop', (e) => {
  e.preventDefault();

  const files = e.dataTransfer.files;
  if (!files.length) return;

  const dataTransfer = new DataTransfer();
  for (let i = 0; i < files.length; i++) {
    dataTransfer.items.add(files[i]);
  }

  fileInput.files = dataTransfer.files;
  storeForm.submit();
  });


  // Browse button click
  if (browseBtn) {
    browseBtn.addEventListener('click', () => {
      fileInput.click();
    });
  }

  // Auto-submit when files are selected via browse
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      storeForm.submit();
    }
  });
}

// Add hand-drawn effect to table rows on hover
const tableRows = document.querySelectorAll('tbody tr');
tableRows.forEach(row => {
  row.addEventListener('mouseenter', function() {
    this.style.transform = 'translateX(5px)';
    this.style.transition = 'transform 0.2s ease';
  });
  
  row.addEventListener('mouseleave', function() {
    this.style.transform = 'translateX(0)';
  });
});

// Add slight animation to sketch boxes
const sketchBoxes = document.querySelectorAll('.sketch-box');
sketchBoxes.forEach(box => {
  box.addEventListener('mouseenter', function() {
    const border = this.querySelector('.sketch-border');
    if (border) {
      border.style.animationDuration = '1s';
    }
  });
  
  box.addEventListener('mouseleave', function() {
    const border = this.querySelector('.sketch-border');
    if (border) {
      border.style.animationDuration = '4s';
    }
  });
});