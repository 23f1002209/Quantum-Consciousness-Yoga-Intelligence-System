class QCYISApp {
    constructor() {
        this.ws = null;
        this.sessionId = this.generateSessionId();
        this.videoElement = document.getElementById('videoElement');
        this.poseCanvas = document.getElementById('poseCanvas');
        this.ctx = this.poseCanvas.getContext('2d');
        this.stream = null;
        this.isDetecting = false;
        this.animationId = null;
        
        // UI Elements
        this.elements = {
            connectionStatus: document.getElementById('connectionStatus'),
            startCamera: document.getElementById('startCamera'),
            stopCamera: document.getElementById('stopCamera'),
            togglePoseDetection: document.getElementById('togglePoseDetection'),
            detectedPose: document.getElementById('detectedPose'),
            qualityScore: document.getElementById('qualityScore'),
            pciScore: document.getElementById('pciScore'),
            meditationDepth: document.getElementById('meditationDepth'),
            coherence: document.getElementById('coherence'),
            correctionsList: document.getElementById('correctionsList'),
            chatInput: document.getElementById('chatInput'),
            sendMessage: document.getElementById('sendMessage'),
            chatMessages: document.getElementById('chatMessages'),
            chatStatus: document.getElementById('chatStatus')
        };
        
        this.init();
    }

    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }

    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.startConsciousnessSimulation();
    }

    setupEventListeners() {
        this.elements.startCamera.addEventListener('click', () => this.startCamera());
        this.elements.stopCamera.addEventListener('click', () => this.stopCamera());
        this.elements.togglePoseDetection.addEventListener('click', () => this.togglePoseDetection());
        this.elements.sendMessage.addEventListener('click', () => this.sendChatMessage());
        this.elements.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendChatMessage();
        });

        this.videoElement.addEventListener('loadedmetadata', () => {
            this.resizeCanvas();
        });

        window.addEventListener('resize', () => {
            this.resizeCanvas();
        });
    }

    connectWebSocket() {
        const wsUrl = `ws://localhost:8000/ws/yoga/${this.sessionId}`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.updateConnectionStatus(true);
            };

            this.ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleWebSocketMessage(message);
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateConnectionStatus(false);
                setTimeout(() => this.connectWebSocket(), 3000);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }

    updateConnectionStatus(connected) {
        const indicator = this.elements.connectionStatus.querySelector('.status-indicator');
        const text = this.elements.connectionStatus.querySelector('.status-text');
        
        if (connected) {
            indicator.classList.add('connected');
            text.textContent = 'Connected';
        } else {
            indicator.classList.remove('connected');
            text.textContent = 'Disconnected';
        }
    }

    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                } 
            });
            
            this.videoElement.srcObject = this.stream;
            this.elements.startCamera.disabled = true;
            this.elements.stopCamera.disabled = false;
            this.elements.togglePoseDetection.disabled = false;
            
            console.log('Camera started successfully');
        } catch (error) {
            console.error('Error starting camera:', error);
            alert('Unable to access camera. Please check permissions.');
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.videoElement.srcObject = null;
            this.stream = null;
        }
        
        this.stopPoseDetection();
        this.elements.startCamera.disabled = false;
        this.elements.stopCamera.disabled = true;
        this.elements.togglePoseDetection.disabled = true;
        this.elements.detectedPose.textContent = 'No pose detected';
        this.elements.qualityScore.textContent = 'Quality: --';
        this.clearCanvas();
    }

    togglePoseDetection() {
        if (this.isDetecting) {
            this.stopPoseDetection();
        } else {
            this.startPoseDetection();
        }
    }

    startPoseDetection() {
        if (!this.stream) {
            alert('Please start the camera first.');
            return;
        }
        this.isDetecting = true;
        this.elements.togglePoseDetection.textContent = 'Stop Pose Detection';
        this.processVideoFrame();
    }

    stopPoseDetection() {
        this.isDetecting = false;
        this.elements.togglePoseDetection.textContent = 'Start Pose Detection';
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.clearCanvas();
    }

    processVideoFrame() {
        if (!this.isDetecting) return;

        this.ctx.drawImage(this.videoElement, 0, 0, this.poseCanvas.width, this.poseCanvas.height);
        const frameData = this.poseCanvas.toDataURL('image/jpeg', 0.8);

        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'pose_frame',
                data: frameData
            }));
        }

        this.animationId = requestAnimationFrame(() => this.processVideoFrame());
    }

    clearCanvas() {
        this.ctx.clearRect(0, 0, this.poseCanvas.width, this.poseCanvas.height);
    }

    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'pose_correction':
                this.updatePoseData(message.data);
                break;
            case 'chat_response':
                this.addChatMessage('assistant', message.data);
                break;
            case 'consciousness_analysis':
                this.updateConsciousnessData(message.data);
                break;
            default:
                console.warn('Unknown message type:', message.type);
        }
    }

    updatePoseData(data) {
        if (!data.pose_detected) {
            this.elements.detectedPose.textContent = 'No pose detected';
            this.elements.qualityScore.textContent = 'Quality: --';
            this.clearCanvas();
            this.clearCorrections();
            return;
        }

        this.elements.detectedPose.textContent = `Pose: ${data.detected_pose}`;
        this.elements.qualityScore.textContent = `Quality: ${data.quality_score}%`;

        this.drawPoseLandmarks(data.landmarks);
        this.updateCorrections(data.corrections);
    }

    drawPoseLandmarks(landmarks) {
        this.clearCanvas();
        this.ctx.strokeStyle = '#00ffff';
        this.ctx.lineWidth = 2;

        landmarks.forEach(point => {
            const x = point.x * this.poseCanvas.width;
            const y = point.y * this.poseCanvas.height;
            this.ctx.beginPath();
            this.ctx.arc(x, y, 5, 0, 2 * Math.PI);
            this.ctx.fillStyle = '#ff00ff';
            this.ctx.fill();
            this.ctx.stroke();
        });
    }

    updateCorrections(corrections) {
        const container = this.elements.correctionsList;
        container.innerHTML = '';

        if (!corrections || corrections.length === 0) {
            container.innerHTML = '<p class="no-corrections">Great form! Keep holding the pose.</p>';
            return;
        }

        corrections.forEach(correction => {
            const div = document.createElement('div');
            div.className = 'correction-item';
            div.textContent = correction;
            container.appendChild(div);
        });
    }

    clearCorrections() {
        this.elements.correctionsList.innerHTML = '<p class="no-corrections">Start pose detection to receive guidance</p>';
    }

    updateConsciousnessData(data) {
        if (!data) return;

        this.elements.pciScore.textContent = data.pci_score !== undefined ? data.pci_score.toFixed(3) : '--';
        this.elements.meditationDepth.textContent = data.meditation_depth ? data.meditation_depth.level : '--';
        this.elements.coherence.textContent = data.overall_coherence !== undefined ? data.overall_coherence.toFixed(3) : '--';

        if (data.quantum_metrics) {
            const coherencePercent = Math.min(100, Math.max(0, data.quantum_metrics.coherence * 100));
            const entanglementPercent = Math.min(100, Math.max(0, data.quantum_metrics.entanglement_strength * 100));
            const processingPower = data.quantum_metrics.processing_power || 0;

            document.getElementById('qubitCoherence').style.width = `${coherencePercent}%`;
            document.getElementById('entanglement').style.width = `${entanglementPercent}%`;
            document.getElementById('processingPower').textContent = processingPower.toFixed(2);
        }

        if (data.chakra_analysis && data.chakra_analysis.chakras) {
            Object.entries(data.chakra_analysis.chakras).forEach(([chakra, info]) => {
                const chakraElem = document.querySelector(`.chakra[data-chakra="${chakra}"] .chakra-indicator`);
                if (chakraElem) {
                    const activation = info.activation || 0;
                    const colorIntensity = Math.min(1, Math.max(0, activation));
                    chakraElem.style.backgroundColor = `rgba(0, 255, 255, ${colorIntensity})`;
                    chakraElem.title = `${chakra.charAt(0).toUpperCase() + chakra.slice(1)} Chakra: ${info.balance}`;
                }
            });
        }
    }

    sendChatMessage() {
        const message = this.elements.chatInput.value.trim();
        if (!message) return;

        this.addChatMessage('user', message);
        this.elements.chatInput.value = '';

        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'chat_message',
                content: message
            }));
        }
    }

    addChatMessage(sender, text) {
        const container = this.elements.chatMessages;
        const messageDiv = document.createElement('div');
        messageDiv.className = sender === 'user' ? 'message user-message' : 'message assistant-message';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;

        messageDiv.appendChild(contentDiv);
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
    }

    resizeCanvas() {
        if (!this.videoElement.videoWidth || !this.videoElement.videoHeight) return;

        this.poseCanvas.width = this.videoElement.videoWidth;
        this.poseCanvas.height = this.videoElement.videoHeight;
    }

    startConsciousnessSimulation() {
        setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ 
                    type: 'consciousness_data', 
                    data: {
                        eeg: {
                            alpha: Math.random() * 12 + 8,
                            theta: Math.random() * 4 + 4,
                            beta: Math.random() * 17 + 13,
                            gamma: Math.random() * 70 + 30
                        },
                        duration: Date.now() / 1000,
                        breathing: {
                            rate: Math.random() * 8 + 8,
                            depth: Math.random() * 0.5 + 0.5
                        }
                    }
                }));
            }
        }, 5000);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.qcyisApp = new QCYISApp();
});
