/**
 * PM-AJAY NSQF Livelihood Platform - Audio Recording & Conversational Assistant Client
 * Handles Web Audio API MediaRecorder, live Bauhaus waveform visualizer,
 * multi-lingual STT API communication, and voice response synthesis.
 */

class VoiceAssistantClient {
  constructor(options = {}) {
    this.sessionId = options.sessionId || ('sess_' + Math.random().toString(36).substring(2, 9));
    this.currentStep = options.initialStep || 1;
    this.language = options.language || 'hi';
    this.beneficiaryId = options.beneficiaryId || null;
    this.onStateChange = options.onStateChange || (() => {});
    this.onNewMessage = options.onNewMessage || (() => {});

    this.mediaRecorder = null;
    this.audioChunks = [];
    this.audioContext = null;
    this.analyser = null;
    this.sourceNode = null;
    this.animFrameId = null;
    this.isRecording = false;
    this.canvas = document.getElementById('waveformCanvas');
    this.canvasCtx = this.canvas ? this.canvas.getContext('2d') : null;

    this.speechSynth = window.speechSynthesis || null;
    this.activeUtterance = null;
  }

  async initAudioStream() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.setupWebAudioAnalyser(stream);

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm';

      this.mediaRecorder = new MediaRecorder(stream, { mimeType });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        this.audioChunks = [];
        await this.handleAudioRecorded(audioBlob);
      };

      return true;
    } catch (err) {
      console.warn('Microphone access not available or denied:', err);
      return false;
    }
  }

  setupWebAudioAnalyser(stream) {
    if (!this.canvas) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.audioContext = new AudioCtx();
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 64;
      this.sourceNode = this.audioContext.createMediaStreamSource(stream);
      this.sourceNode.connect(this.analyser);
      this.drawWaveform();
    } catch (e) {
      console.error('AudioContext error:', e);
    }
  }

  drawWaveform() {
    if (!this.canvasCtx || !this.analyser) return;

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const render = () => {
      this.animFrameId = requestAnimationFrame(render);
      this.analyser.getByteFrequencyData(dataArray);

      const width = this.canvas.width;
      const height = this.canvas.height;
      this.canvasCtx.fillStyle = '#111111';
      this.canvasCtx.fillRect(0, 0, width, height);

      const barWidth = (width / bufferLength) * 1.5;
      let barX = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * height;

        // Alternate Bauhaus geometric bars: Navy Blue and Saffron
        if (i % 2 === 0) {
          this.canvasCtx.fillStyle = '#FF671F';
        } else {
          this.canvasCtx.fillStyle = '#06038D';
        }

        // Draw solid geometric block
        this.canvasCtx.fillRect(barX, height - barHeight, barWidth - 2, barHeight);
        barX += barWidth;
      }
    };

    render();
  }

  startRecording() {
    if (this.speechSynth && this.speechSynth.speaking) {
      this.speechSynth.cancel();
    }

    if (this.mediaRecorder && this.mediaRecorder.state === 'inactive') {
      this.audioChunks = [];
      this.mediaRecorder.start(250);
      this.isRecording = true;
      this.onStateChange({ isRecording: true });
    }
  }

  stopRecording() {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
      this.isRecording = false;
      this.onStateChange({ isRecording: false });
    }
  }

  async handleAudioRecorded(audioBlob) {
    this.onStateChange({ isProcessing: true });
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'voice_input.webm');
      formData.append('language', this.language);

      const sttResp = await fetch('/api/stt/transcribe/', {
        method: 'POST',
        body: formData
      });

      const sttJson = await sttResp.json();
      const transcribedText = sttJson.data?.text || '';

      if (transcribedText) {
        this.onNewMessage({
          sender: 'user',
          text: transcribedText,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });

        await this.sendChatMessage(transcribedText);
      }
    } catch (err) {
      console.error('STT API Error:', err);
    } finally {
      this.onStateChange({ isProcessing: false });
    }
  }

  async sendChatMessage(text) {
    this.onStateChange({ isProcessing: true });
    try {
      const resp = await fetch('/api/interview/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: this.sessionId,
          step: this.currentStep,
          language: this.language,
          text: text,
          beneficiary_id: this.beneficiaryId
        })
      });

      const data = await resp.json();
      if (data.success) {
        this.beneficiaryId = data.beneficiary_id;
        this.currentStep = data.next_step;

        const nextPrompt = data.next_prompt;
        this.onNewMessage({
          sender: 'agent',
          text: nextPrompt.text,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });

        // Trigger TTS voice output
        if (data.tts) {
          this.speakText(data.tts.text, data.tts.voice_lang_tag);
        }

        this.onStateChange({
          currentStep: this.currentStep,
          isCompleted: data.is_completed,
          beneficiaryProfile: data.beneficiary_profile,
          beneficiaryId: this.beneficiaryId
        });
      }
    } catch (e) {
      console.error('Chat API Error:', e);
    } finally {
      this.onStateChange({ isProcessing: false });
    }
  }

  speakText(text, langTag = 'hi-IN') {
    if (!this.speechSynth) return;
    this.speechSynth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langTag;
    utterance.rate = 0.95;
    utterance.pitch = 1.05;

    // Pick best matching Indic voice if available
    const voices = this.speechSynth.getVoices();
    const matchedVoice = voices.find(v => v.lang.startsWith(langTag.split('-')[0]));
    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    utterance.onstart = () => {
      this.onStateChange({ isSpeaking: true });
    };

    utterance.onend = () => {
      this.onStateChange({ isSpeaking: false });
    };

    this.speechSynth.speak(utterance);
  }

  stopSpeaking() {
    if (this.speechSynth) {
      this.speechSynth.cancel();
      this.onStateChange({ isSpeaking: false });
    }
  }
}

window.VoiceAssistantClient = VoiceAssistantClient;
