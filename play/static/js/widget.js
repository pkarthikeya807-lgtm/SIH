/**
 * PM-AJAY Bauhaus Pop-Out Screen Reader Widget (widget.js)
 * Standalone, zero-dependency injectable script.
 * Provides live high-contrast DOM visual highlighting and regional Indic TTS.
 */

(function () {
  'use strict';

  // Prevent multiple injections
  if (window.__PMAJAY_WIDGET_LOADED__) return;
  window.__PMAJAY_WIDGET_LOADED__ = true;

  const LANGUAGES = [
    { code: 'hi', tag: 'hi-IN', label: 'हिन्दी (Hindi)' },
    { code: 'ta', tag: 'ta-IN', label: 'தமிழ் (Tamil)' },
    { code: 'te', tag: 'te-IN', label: 'తెలుగు (Telugu)' },
    { code: 'mr', tag: 'mr-IN', label: 'मराठी (Marathi)' },
    { code: 'or', tag: 'or-IN', label: 'ଓଡ଼ିଆ (Odia)' },
    { code: 'bn', tag: 'bn-IN', label: 'বাংলা (Bengali)' },
    { code: 'en', tag: 'en-IN', label: 'English (India)' }
  ];

  class BauhausScreenReaderWidget {
    constructor() {
      this.selectedLang = 'hi-IN';
      this.rate = 1.0;
      this.pitch = 1.0;
      this.synth = window.speechSynthesis || null;
      this.isReadingPage = false;
      this.domElementsToRead = [];
      this.currentElementIndex = -1;
      this.highlightClass = 'bauhaus-screen-reader-highlight';

      this.injectStyles();
      this.createWidgetUI();
      this.bindSelectionListener();
    }

    injectStyles() {
      const style = document.createElement('style');
      style.id = 'pmajay-widget-styles';
      style.textContent = `
        .pmajay-reader-fab {
          position: fixed;
          bottom: 24px;
          right: 24px;
          z-index: 999999;
          background: #FF671F;
          color: #111111;
          border: 3.5px solid #111111;
          padding: 12px 18px;
          font-family: 'Inter', -apple-system, sans-serif;
          font-size: 14px;
          font-weight: 900;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 8px;
          box-shadow: none !important;
          transition: transform 0.05s ease, background 0.1s ease;
          user-select: none;
        }
        .pmajay-reader-fab:active {
          transform: translate(3px, 3px);
        }
        .pmajay-reader-fab:hover {
          background: #FF9933;
        }
        .pmajay-reader-modal {
          position: fixed;
          bottom: 80px;
          right: 24px;
          width: 320px;
          background: #F5F2EB;
          border: 4px solid #111111;
          z-index: 999999;
          font-family: 'Inter', -apple-system, sans-serif;
          display: none;
          flex-direction: column;
          box-shadow: none !important;
        }
        .pmajay-reader-modal.open {
          display: flex;
        }
        .pmajay-modal-header {
          background: #06038D;
          color: #FFFFFF;
          padding: 10px 14px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 3px solid #111111;
          font-weight: 900;
          font-size: 13px;
          text-transform: uppercase;
        }
        .pmajay-modal-body {
          padding: 14px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .pmajay-select {
          background: #FFFFFF;
          border: 2px solid #111111;
          padding: 8px;
          font-weight: 700;
          font-size: 12px;
          cursor: pointer;
          outline: none;
          width: 100%;
        }
        .pmajay-btn-group {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
        }
        .pmajay-btn {
          border: 2.5px solid #111111;
          background: #FFFFFF;
          color: #111111;
          padding: 8px 10px;
          font-weight: 800;
          font-size: 12px;
          text-transform: uppercase;
          cursor: pointer;
          text-align: center;
        }
        .pmajay-btn:active {
          transform: translate(2px, 2px);
        }
        .pmajay-btn.primary {
          background: #06038D;
          color: #FFFFFF;
        }
        .pmajay-btn.accent {
          background: #FF671F;
          color: #111111;
        }
        .pmajay-btn.danger {
          background: #D32F2F;
          color: #FFFFFF;
        }
        .pmajay-status {
          font-family: monospace;
          font-size: 11px;
          font-weight: bold;
          padding: 6px;
          background: #FFFFFF;
          border: 1.5px solid #111111;
          text-align: center;
        }
        .${this.highlightClass} {
          outline: 4px solid #FF671F !important;
          background-color: #FFF3CD !important;
          transition: outline 0.1s ease, background-color 0.1s ease;
        }
      `;
      document.head.appendChild(style);
    }

    createWidgetUI() {
      // FAB Button
      const fab = document.createElement('button');
      fab.className = 'pmajay-reader-fab';
      fab.id = 'pmajayFab';
      fab.innerHTML = `<span>🔊</span> <span>PM-AJAY Audio</span>`;
      fab.addEventListener('click', () => this.toggleModal());
      document.body.appendChild(fab);

      // Pop-Out Modal
      const modal = document.createElement('div');
      modal.className = 'pmajay-reader-modal';
      modal.id = 'pmajayModal';

      const optionsHtml = LANGUAGES.map(
        l => `<option value="${l.tag}">${l.label}</option>`
      ).join('');

      modal.innerHTML = `
        <div class="pmajay-modal-header">
          <span>🔊 Screen Reader & Audio</span>
          <button style="background:none;border:none;color:#FFF;font-weight:900;cursor:pointer;font-size:16px;" id="pmajayCloseModal">✕</button>
        </div>
        <div class="pmajay-modal-body">
          <label style="font-size:11px;font-weight:900;text-transform:uppercase;">Language / भाषा:</label>
          <select class="pmajay-select" id="pmajayLangSelect">${optionsHtml}</select>

          <div class="pmajay-btn-group">
            <button class="pmajay-btn primary" id="pmajayReadPage">📖 Read Page</button>
            <button class="pmajay-btn accent" id="pmajayReadSelection">🎯 Selection</button>
          </div>

          <div class="pmajay-btn-group">
            <button class="pmajay-btn" id="pmajayPauseResume">⏸ Pause</button>
            <button class="pmajay-btn danger" id="pmajayStop">⏹ Stop</button>
          </div>

          <div class="pmajay-status" id="pmajayStatus">Ready: Select text or click Read Page</div>
        </div>
      `;

      document.body.appendChild(modal);

      // Event bindings
      document.getElementById('pmajayCloseModal').addEventListener('click', () => this.toggleModal(false));
      document.getElementById('pmajayLangSelect').addEventListener('change', (e) => {
        this.selectedLang = e.target.value;
      });
      document.getElementById('pmajayReadPage').addEventListener('click', () => this.startPageReader());
      document.getElementById('pmajayReadSelection').addEventListener('click', () => this.readSelectedText());
      document.getElementById('pmajayPauseResume').addEventListener('click', () => this.togglePause());
      document.getElementById('pmajayStop').addEventListener('click', () => this.stopReading());
    }

    toggleModal(forceState) {
      const modal = document.getElementById('pmajayModal');
      if (forceState !== undefined) {
        modal.classList.toggle('open', forceState);
      } else {
        modal.classList.toggle('open');
      }
    }

    updateStatus(msg) {
      const statusEl = document.getElementById('pmajayStatus');
      if (statusEl) statusEl.textContent = msg;
    }

    bindSelectionListener() {
      document.addEventListener('mouseup', () => {
        const selection = window.getSelection().toString().trim();
        if (selection.length > 5 && !this.isReadingPage) {
          this.updateStatus(`Selected: "${selection.substring(0, 24)}..."`);
        }
      });
    }

    readSelectedText() {
      const selected = window.getSelection().toString().trim();
      if (!selected) {
        this.updateStatus('Please highlight some text first.');
        return;
      }
      this.speak(selected, () => {
        this.updateStatus('Finished reading selection.');
      });
    }

    startPageReader() {
      this.stopReading();
      this.isReadingPage = true;

      // Extract readable DOM elements
      const candidates = Array.from(document.querySelectorAll('h1, h2, h3, h4, p, li, .chat-bubble, .trade-card'));
      this.domElementsToRead = candidates.filter(el => {
        const text = el.innerText.trim();
        return text.length > 8 && !el.closest('.pmajay-reader-modal') && !el.closest('.pmajay-reader-fab');
      });

      this.currentElementIndex = 0;
      this.updateStatus(`Reading element 1 of ${this.domElementsToRead.length}...`);
      this.readNextDOMElement();
    }

    readNextDOMElement() {
      if (!this.isReadingPage || this.currentElementIndex >= this.domElementsToRead.length) {
        this.stopReading();
        this.updateStatus('Finished reading page content.');
        return;
      }

      // Clear previous highlights
      document.querySelectorAll('.' + this.highlightClass).forEach(el => el.classList.remove(this.highlightClass));

      const el = this.domElementsToRead[this.currentElementIndex];
      el.classList.add(this.highlightClass);
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });

      const text = el.innerText.trim();
      this.updateStatus(`Reading: ${this.currentElementIndex + 1}/${this.domElementsToRead.length}`);

      this.speak(text, () => {
        this.currentElementIndex++;
        if (this.isReadingPage) {
          setTimeout(() => this.readNextDOMElement(), 350);
        }
      });
    }

    speak(text, onComplete) {
      if (!this.synth) {
        this.updateStatus('Web Speech API not supported.');
        return;
      }

      this.synth.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = this.selectedLang;
      utterance.rate = this.rate;
      utterance.pitch = this.pitch;

      const voices = this.synth.getVoices();
      const prefix = this.selectedLang.split('-')[0];
      const match = voices.find(v => v.lang.startsWith(prefix));
      if (match) utterance.voice = match;

      utterance.onend = () => {
        if (onComplete) onComplete();
      };

      utterance.onerror = (e) => {
        console.warn('Speech error:', e);
        if (onComplete) onComplete();
      };

      this.synth.speak(utterance);
    }

    togglePause() {
      if (!this.synth) return;
      const pauseBtn = document.getElementById('pmajayPauseResume');
      if (this.synth.paused) {
        this.synth.resume();
        pauseBtn.textContent = '⏸ Pause';
        this.updateStatus('Resumed playback.');
      } else if (this.synth.speaking) {
        this.synth.pause();
        pauseBtn.textContent = '▶ Resume';
        this.updateStatus('Playback paused.');
      }
    }

    stopReading() {
      this.isReadingPage = false;
      if (this.synth) this.synth.cancel();
      document.querySelectorAll('.' + this.highlightClass).forEach(el => el.classList.remove(this.highlightClass));
      const pauseBtn = document.getElementById('pmajayPauseResume');
      if (pauseBtn) pauseBtn.textContent = '⏸ Pause';
      this.updateStatus('Stopped.');
    }
  }

  // Auto-initialize when ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new BauhausScreenReaderWidget());
  } else {
    new BauhausScreenReaderWidget();
  }
})();
