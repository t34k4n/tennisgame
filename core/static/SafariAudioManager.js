class SafariAudioManager {
    constructor(audioId = 'menuMusic', iconId = 'muteIcon') {
        this.audioId = audioId;
        this.iconId = iconId;

        this.isEnabled = true;
        this.isPlaying = false;
        this.volume = 0.3;
        this.savedTime = 0;

        this.audio = this.getOrCreatePersistentAudioElement();
        this.icon = document.getElementById(this.iconId);

        this.init();
    }

    getOrCreatePersistentAudioElement() {
        const isGamePage = window.location.pathname.includes('game.html');
        let audio = document.getElementById(this.audioId);

        if (!audio && !isGamePage) {
            audio = document.createElement('audio');
            audio.id = this.audioId;
            audio.loop = true;
            audio.innerHTML = `<source src="/static/menu.mp3" type="audio/mpeg">`;
            audio.volume = this.volume;
            document.body.appendChild(audio);
            window.__globalMenuMusic = audio;
        }

        // Eğer önceden oluşturulmuşsa globalden al
        if (!audio && window.__globalMenuMusic) {
            audio = window.__globalMenuMusic;
        }

        return audio;
    }

    init() {
        if (!this.audio) return;

        this.loadSettings();
        this.audio.loop = true;

        if (this.savedTime > 0) {
            this.audio.currentTime = this.savedTime;
        }

        if (this.shouldAutoPlay()) {
            this.startMusic();
        }

        if (this.icon) {
            this.icon.addEventListener('click', () => this.toggleMusic());
        }

        this.audio.addEventListener('play', () => {
            this.isPlaying = true;
            this.updateIcon();
        });

        this.audio.addEventListener('pause', () => {
            this.isPlaying = false;
            this.updateIcon();
        });

        this.audio.addEventListener('error', (e) => {
            console.error('Audio error:', e);
        });

        this.checkAudioReadiness();
        this.setupUserInteractionListener();
        this.updateIcon();

        window.addEventListener('beforeunload', () => this.beforeUnload());
    }

    stopAndRemoveMenuMusic() {
        const audio = document.getElementById('menuMusic');
        if (audio) {
            audio.pause();
            audio.remove();
            window.__globalMenuMusic = null;
        }
    }

    checkAudioReadiness() {
        if (typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined') {
            const AudioContextClass = AudioContext || webkitAudioContext;
            try {
                const audioContext = new AudioContextClass();
                this.isEnabled = audioContext.state !== 'suspended';
            } catch {
                this.isEnabled = false;
            }
        }
    }

    setupUserInteractionListener() {
        const enableAudio = async () => {
            try {
                if (typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined') {
                    const AudioContextClass = AudioContext || webkitAudioContext;
                    const audioContext = new AudioContextClass();
                    if (audioContext.state === 'suspended') {
                        await audioContext.resume();
                    }
                }

                if (this.savedTime > 0) {
                    this.audio.currentTime = this.savedTime;
                }

                this.isEnabled = true;
                if (this.shouldAutoPlay()) {
                    await this.startMusic();
                }

                document.removeEventListener('click', enableAudio);
                document.removeEventListener('touchstart', enableAudio);
                document.removeEventListener('keydown', enableAudio);
            } catch (error) {
                console.error('Enable audio failed:', error);
            }
        };

        document.addEventListener('click', enableAudio, { once: true });
        document.addEventListener('touchstart', enableAudio, { once: true });
        document.addEventListener('keydown', enableAudio, { once: true });
    }

    shouldAutoPlay() {
        const saved = localStorage.getItem('audioSettings');
        if (saved) {
            const settings = JSON.parse(saved);
            return settings.isPlaying !== false;
        }
        return true;
    }

    async toggleMusic() {
        if (!this.isEnabled) return;

        if (this.audio.paused) {
            await this.startMusic();
        } else {
            this.stopMusic();
        }
    }

    async startMusic() {
        try {
            if (!this.isEnabled) return;
            if (this.savedTime > 0) {
                this.audio.currentTime = this.savedTime;
            }
            await this.audio.play();
            this.isPlaying = true;
        } catch (error) {
            console.error('Failed to play:', error);
            if (error.name === 'NotAllowedError') {
                this.isEnabled = false;
                this.setupUserInteractionListener();
            }
        }
    }

    stopMusic() {
        this.savedTime = this.audio.currentTime;
        this.audio.pause();
        this.isPlaying = false;
    }

    updateIcon() {
        if (!this.icon) return;
        if (this.isPlaying && !this.audio.paused) {
            this.icon.src = this.icon.src.replace('speaker_icon_muted', 'speaker_icon');
        } else {
            this.icon.src = this.icon.src.replace('speaker_icon.', 'speaker_icon_muted.');
        }
    }

    saveSettings() {
        localStorage.setItem('audioSettings', JSON.stringify({
            isPlaying: this.isPlaying,
            volume: this.volume,
            savedTime: this.audio.currentTime || this.savedTime,
            isEnabled: this.isEnabled
        }));
    }

    loadSettings() {
        const saved = localStorage.getItem('audioSettings');
        if (saved) {
            try {
                const settings = JSON.parse(saved);
                this.volume = settings.volume ?? 0.3;
                this.savedTime = settings.savedTime || 0;
                this.isEnabled = settings.isEnabled ?? true;
                this.audio.muted = settings.isPlaying === false;
            } catch {
                console.error('Failed to load settings');
            }
        }
    }

    beforeUnload() {
        this.saveSettings();
    }
}

// Init
let audioManager;
document.addEventListener('DOMContentLoaded', () => {
    const isGamePage = window.location.pathname.includes('game.html');

    if (isGamePage) {
        audioManager = new SafariAudioManager('gameMusic', 'muteIcon');
        audioManager.stopAndRemoveMenuMusic();
    } else {
        audioManager = new SafariAudioManager('menuMusic', 'muteIcon');
    }
});

function toggleMusic() {
    if (audioManager) audioManager.toggleMusic();
}
