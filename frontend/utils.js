// Utility functions for QCYIS application

class QCYISUtils {
    static calculateAngle(a, b, c) {
        const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
        let angle = Math.abs(radians * 180.0 / Math.PI);
        if (angle > 180.0) {
            angle = 360 - angle;
        }
        return angle;
    }

    static normalizeCoordinates(landmarks, width, height) {
        return landmarks.map(landmark => ({
            x: landmark.x * width,
            y: landmark.y * height,
            z: landmark.z
        }));
    }

    static smoothData(newValue, oldValue, smoothingFactor = 0.8) {
        return oldValue * smoothingFactor + newValue * (1 - smoothingFactor);
    }

    static formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    static generateSessionReport(sessionData) {
        return {
            duration: this.formatTime(sessionData.duration),
            averageQuality: sessionData.qualityScores.reduce((a, b) => a + b, 0) / sessionData.qualityScores.length,
            posesDetected: sessionData.posesDetected.length,
            improvements: sessionData.improvements || []
        };
    }

    static validatePoseData(data) {
        return data && 
               typeof data.pose_detected === 'boolean' &&
               Array.isArray(data.landmarks) &&
               typeof data.quality_score === 'number';
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    static isWebRTCSupported() {
        return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    }

    static isWebSocketSupported() {
        return 'WebSocket' in window || 'MozWebSocket' in window;
    }

    static getDeviceCapabilities() {
        return {
            webRTC: this.isWebRTCSupported(),
            webSocket: this.isWebSocketSupported(),
            canvas: !!document.createElement('canvas').getContext,
            localStorage: typeof Storage !== 'undefined'
        };
    }

    static saveToLocalStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
            return false;
        }
    }

    static loadFromLocalStorage(key) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Failed to load from localStorage:', error);
            return null;
        }
    }

    static exportSessionData(sessionData, format = 'json') {
        const data = JSON.stringify(sessionData, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `qcyis-session-${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    static calculatePoseAccuracy(detectedAngles, referenceAngles) {
        let totalError = 0;
        let jointCount = 0;

        for (const joint in referenceAngles) {
            if (detectedAngles[joint] !== undefined) {
                const error = Math.abs(detectedAngles[joint] - referenceAngles[joint]);
                totalError += error;
                jointCount++;
            }
        }

        if (jointCount === 0) return 0;
        const averageError = totalError / jointCount;
        return Math.max(0, 100 - (averageError / 180 * 100));
    }

    static generateFeedback(accuracy, pose) {
        if (accuracy >= 90) {
            return `Excellent ${pose} pose! Your form is nearly perfect.`;
        } else if (accuracy >= 75) {
            return `Good ${pose} pose. Minor adjustments could improve your alignment.`;
        } else if (accuracy >= 60) {
            return `Fair ${pose} pose. Focus on the highlighted corrections.`;
        } else {
            return `Keep practicing your ${pose} pose. Check the guidance for improvements.`;
        }
    }
}

window.QCYISUtils = QCYISUtils;
