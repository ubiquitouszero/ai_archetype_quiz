/**
 * AI Archetype Quiz - Production Application
 * Integrated with FastAPI backend for acceleratinghumans.com
 */

class QuizApp {
    constructor() {
        this.currentQuestionIndex = 0;
        this.answers = {};
        this.startTime = null;
        this.quizData = null;
        this.sessionId = null;
        this.results = null;
        
        this.init();
    }

    async init() {
        try {
            // Get quiz data from window (embedded in template) or API
            this.quizData = window.QUIZ_DATA || await this.loadQuizData();
            
            if (!this.quizData || !this.quizData.questions) {
                throw new Error('Quiz data not available');
            }

            this.bindEvents();
            this.showScreen('welcome-screen');
            
            // Log page view
            await this.logAnalytics('page_view', { page: 'welcome' });
            
        } catch (error) {
            console.error('Failed to initialize quiz:', error);
            this.showError('Failed to load quiz. Please refresh the page.');
        }
    }

    async loadQuizData() {
        try {
            const response = await fetch('/api/quiz/data');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Failed to load quiz data:', error);
            throw error;
        }
    }

    bindEvents() {
        // Welcome screen
        document.getElementById('start-quiz-btn')?.addEventListener('click', () => {
            this.startQuiz();
        });

        // Quiz navigation
        document.getElementById('prev-btn')?.addEventListener('click', () => {
            this.previousQuestion();
        });

        document.getElementById('next-btn')?.addEventListener('click', () => {
            this.nextQuestion();
        });

        // Results screen
        document.getElementById('retake-btn')?.addEventListener('click', () => {
            this.resetQuiz();
        });

        document.getElementById('share-btn')?.addEventListener('click', () => {
            this.shareResults();
        });

        document.getElementById('summary-btn')?.addEventListener('click', () => {
            window.location.href = '/summary';
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (this.getCurrentScreen() === 'quiz-screen') {
                if (e.key === 'ArrowLeft' && !document.getElementById('prev-btn').disabled) {
                    this.previousQuestion();
                } else if (e.key === 'ArrowRight' && !document.getElementById('next-btn').disabled) {
                    this.nextQuestion();
                }
            }
        });
    }

    showScreen(screenId) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });

        // Show target screen
        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.classList.add('active');
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    getCurrentScreen() {
        const activeScreen = document.querySelector('.screen.active');
        return activeScreen ? activeScreen.id : null;
    }

    async startQuiz() {
        try {
            this.currentQuestionIndex = 0;
            this.answers = {};
            this.startTime = Date.now();
            
            await this.logAnalytics('quiz_started');
            
            this.showScreen('quiz-screen');
            this.displayQuestion();
            
        } catch (error) {
            console.error('Error starting quiz:', error);
            this.showError('Failed to start quiz. Please try again.');
        }
    }

    displayQuestion() {
        const question = this.quizData.questions[this.currentQuestionIndex];
        const questionNumber = this.currentQuestionIndex + 1;
        const totalQuestions = this.quizData.questions.length;
        
        // Update progress
        const progress = (questionNumber / totalQuestions) * 100;
        document.getElementById('progress-fill').style.width = `${progress}%`;
        document.getElementById('progress-text').textContent = 
            `Question ${questionNumber} of ${totalQuestions}`;
        
        // Update estimated time remaining
        const remainingQuestions = totalQuestions - questionNumber;
        const estimatedMinutes = Math.ceil(remainingQuestions * 0.3); // ~18 seconds per question
        document.getElementById('progress-time').textContent = 
            estimatedMinutes > 0 ? `~${estimatedMinutes} min remaining` : 'Almost done!';

        // Display question
        document.getElementById('question-text').textContent = question.question;

        // Display options
        this.renderOptions(question);

        // Update navigation buttons
        this.updateNavigationButtons();
    }

    renderOptions(question) {
        const optionsContainer = document.getElementById('options-container');
        optionsContainer.innerHTML = '';

        Object.entries(question.answers).forEach(([letter, text]) => {
            const optionElement = document.createElement('div');
            optionElement.className = 'option-item';
            optionElement.setAttribute('tabindex', '0');
            optionElement.setAttribute('role', 'button');
            optionElement.setAttribute('aria-pressed', 'false');
            
            optionElement.innerHTML = `
                <div class="option-letter">${letter}</div>
                <div class="option-text">${text}</div>
            `;

            // Check if this option was previously selected
            if (this.answers[question.id] === letter) {
                optionElement.classList.add('selected');
                optionElement.setAttribute('aria-pressed', 'true');
            }

            // Click handler
            optionElement.addEventListener('click', () => {
                this.selectOption(question.id, letter, optionElement);
            });

            // Keyboard handler
            optionElement.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.selectOption(question.id, letter, optionElement);
                }
            });

            optionsContainer.appendChild(optionElement);
        });
    }

    async selectOption(questionId, letter, optionElement) {
        try {
            // Remove previous selection
            document.querySelectorAll('.option-item').forEach(item => {
                item.classList.remove('selected');
                item.setAttribute('aria-pressed', 'false');
            });

            // Add selection to clicked option
            optionElement.classList.add('selected');
            optionElement.setAttribute('aria-pressed', 'true');

            // Store answer
            this.answers[questionId] = letter;

            // Log answer selection
            await this.logAnalytics('question_answered', {
                question_id: questionId,
                answer: letter,
                question_number: this.currentQuestionIndex + 1
            });

            // Update navigation buttons
            this.updateNavigationButtons();
            
            // Add subtle haptic feedback on mobile
            if ('vibrate' in navigator) {
                navigator.vibrate(50);
            }
            
        } catch (error) {
            console.error('Error selecting option:', error);
        }
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const currentQuestion = this.quizData.questions[this.currentQuestionIndex];
        const hasAnswer = this.answers[currentQuestion.id];

        // Previous button
        prevBtn.disabled = this.currentQuestionIndex === 0;

        // Next button
        if (this.currentQuestionIndex === this.quizData.questions.length - 1) {
            nextBtn.innerHTML = `
                Calculate Results
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4.16667 10H15.8333M15.8333 10L10.8333 5M15.8333 10L10.8333 15" stroke="currentColor" stroke-width="1.67" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            `;
        } else {
            nextBtn.innerHTML = `
                Next
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4.16667 10H15.8333M15.8333 10L10.8333 5M15.8333 10L10.8333 15" stroke="currentColor" stroke-width="1.67" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            `;
        }
        
        nextBtn.disabled = !hasAnswer;
    }

    async previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.displayQuestion();
            
            await this.logAnalytics('question_navigation', {
                direction: 'previous',
                question_number: this.currentQuestionIndex + 1
            });
        }
    }

    async nextQuestion() {
        if (this.currentQuestionIndex < this.quizData.questions.length - 1) {
            this.currentQuestionIndex++;
            this.displayQuestion();
            
            await this.logAnalytics('question_navigation', {
                direction: 'next',
                question_number: this.currentQuestionIndex + 1
            });
        } else {
            await this.finishQuiz();
        }
    }

    async finishQuiz() {
        try {
            this.showLoading('Calculating your AI archetype...');
            
            const endTime = Date.now();
            const completionTimeSeconds = (endTime - this.startTime) / 1000;
            
            // Submit quiz to backend
            const response = await fetch('/api/quiz/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    responses: this.answers,
                    completion_time: completionTimeSeconds,
                    referrer: document.referrer
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            this.results = await response.json();
            this.sessionId = this.results.session_id;
            
            this.hideLoading();
            this.showScreen('results-screen');
            this.displayResults();
            
            // Log completion
            await this.logAnalytics('quiz_completed', {
                session_id: this.sessionId,
                archetype: this.results.primary_archetype,
                archetype_name: this.results.archetype_name,
                completion_time: completionTimeSeconds
            });
            
        } catch (error) {
            this.hideLoading();
            console.error('Error submitting quiz:', error);
            this.showError('Failed to calculate results. Please try again.');
        }
    }

    displayResults() {
        if (!this.results) return;

        const { 
            primary_archetype, 
            archetype_name, 
            scores, 
            archetype_data, 
            share_url 
        } = this.results;

        // Update primary archetype display
        document.getElementById('archetype-icon').textContent = archetype_data.icon || '🤖';
        document.getElementById('archetype-name').textContent = archetype_name;
        document.getElementById('archetype-description').textContent = archetype_data.description;
        document.getElementById('primary-score-display').textContent = `${scores[primary_archetype]}%`;

        // Update characteristics
        this.renderCharacteristics(archetype_data.characteristics);

        // Update insights
        document.getElementById('work-approach').textContent = archetype_data.approach;
        document.getElementById('change-response').textContent = archetype_data.change_response;
        document.getElementById('archetype-risks').textContent = archetype_data.risks;

        // Update score breakdown
        this.renderScoreBreakdown(scores);

        // Store share URL for sharing
        this.shareUrl = share_url;

        // Add visual enhancements
        this.addResultsAnimations();
    }

    renderCharacteristics(characteristics) {
        const characteristicsList = document.getElementById('characteristics-list');
        characteristicsList.innerHTML = '';
        
        characteristics.forEach((characteristic, index) => {
            const li = document.createElement('li');
            li.textContent = characteristic;
            li.style.animationDelay = `${index * 100}ms`;
            li.classList.add('fade-in-up');
            characteristicsList.appendChild(li);
        });
    }

    renderScoreBreakdown(scores) {
        const breakdownChart = document.getElementById('breakdown-chart');
        breakdownChart.innerHTML = '';

        // Sort archetypes by score (highest first)
        const sortedScores = Object.entries(scores)
            .sort(([,a], [,b]) => b - a)
            .filter(([,score]) => score > 0);

        sortedScores.forEach(([letter, score], index) => {
            const archetype = this.quizData.archetypes[letter];
            
            const breakdownItem = document.createElement('div');
            breakdownItem.className = 'breakdown-item';
            breakdownItem.style.animationDelay = `${index * 150}ms`;
            
            breakdownItem.innerHTML = `
                <div class="breakdown-info">
                    <div class="breakdown-label">
                        <span class="breakdown-icon">${archetype.icon}</span>
                        <span class="breakdown-name">${archetype.name}</span>
                    </div>
                    <div class="breakdown-percentage">${score}%</div>
                </div>
                <div class="breakdown-bar">
                    <div class="breakdown-fill" 
                         style="width: ${score}%; background-color: ${archetype.color}; animation-delay: ${index * 150 + 300}ms;">
                    </div>
                </div>
            `;

            breakdownChart.appendChild(breakdownItem);
        });
    }

    addResultsAnimations() {
        // Add staggered animations to results elements
        const animatedElements = document.querySelectorAll('.results-screen .fade-in-up');
        animatedElements.forEach((el, index) => {
            el.style.animationDelay = `${index * 100}ms`;
        });

        // Animate score ring
        const scoreRing = document.querySelector('.archetype-score-ring');
        if (scoreRing) {
            const score = this.results.scores[this.results.primary_archetype];
            const circumference = 2 * Math.PI * 45; // radius = 45
            const offset = circumference - (score / 100) * circumference;
            
            setTimeout(() => {
                scoreRing.style.strokeDasharray = circumference;
                scoreRing.style.strokeDashoffset = offset;
            }, 500);
        }
    }

    async shareResults() {
        try {
            if (!this.shareUrl) {
                this.showError('No results to share yet.');
                return;
            }

            const shareData = {
                title: `My AI Archetype: ${this.results.archetype_name}`,
                text: `I just discovered I'm "${this.results.archetype_name}" on the AI Archetype Quiz! ${this.results.archetype_data.description} Take the quiz to find your AI personality:`,
                url: this.shareUrl
            };

            // Try native sharing first
            if (navigator.share && navigator.canShare(shareData)) {
                await navigator.share(shareData);
                await this.logAnalytics('result_shared', { method: 'native' });
            } else {
                // Fallback to clipboard
                const shareText = `${shareData.text} ${shareData.url}`;
                await navigator.clipboard.writeText(shareText);
                this.showToast('Results link copied to clipboard!');
                await this.logAnalytics('result_shared', { method: 'clipboard' });
            }
        } catch (error) {
            console.error('Error sharing results:', error);
            
            // Final fallback - show share URL
            this.showShareModal();
        }
    }

    showShareModal() {
        const modal = document.createElement('div');
        modal.className = 'share-modal-overlay';
        modal.innerHTML = `
            <div class="share-modal">
                <h3>Share Your Results</h3>
                <p>Copy this link to share your AI archetype:</p>
                <div class="share-url-container">
                    <input type="text" value="${this.shareUrl}" readonly id="share-url-input">
                    <button class="btn btn--secondary" id="copy-url-btn">Copy</button>
                </div>
                <button class="btn btn--outline" id="close-share-modal">Close</button>
            </div>
        `;

        document.body.appendChild(modal);

        // Event handlers
        document.getElementById('copy-url-btn').addEventListener('click', async () => {
            const input = document.getElementById('share-url-input');
            input.select();
            document.execCommand('copy');
            this.showToast('Link copied!');
            await this.logAnalytics('result_shared', { method: 'modal' });
        });

        document.getElementById('close-share-modal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }

    async resetQuiz() {
        try {
            await this.logAnalytics('quiz_reset');
            
            this.currentQuestionIndex = 0;
            this.answers = {};
            this.results = null;
            this.sessionId = null;
            this.shareUrl = null;
            
            this.showScreen('welcome-screen');
        } catch (error) {
            console.error('Error resetting quiz:', error);
        }
    }

    // Utility Methods
    showLoading(message = 'Loading...') {
        const loadingOverlay = document.getElementById('loading-overlay');
        const loadingText = document.querySelector('.loading-text');
        
        if (loadingText) {
            loadingText.textContent = message;
        }
        
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }
    }

    hideLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.textContent = message;

        const container = document.getElementById('toast-container');
        if (container) {
            container.appendChild(toast);

            // Show toast
            setTimeout(() => toast.classList.add('show'), 100);

            // Hide and remove toast
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => {
                    if (container.contains(toast)) {
                        container.removeChild(toast);
                    }
                }, 300);
            }, 4000);
        } else {
            // Fallback to alert
            alert(message);
        }
    }

    async logAnalytics(eventType, data = {}) {
        try {
            // Don't block the UI for analytics
            fetch('/api/analytics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event_type: eventType,
                    session_id: this.sessionId,
                    data: {
                        ...data,
                        timestamp: new Date().toISOString(),
                        user_agent: navigator.userAgent,
                        screen_resolution: `${screen.width}x${screen.height}`,
                        viewport_size: `${window.innerWidth}x${window.innerHeight}`
                    }
                })
            }).catch(error => {
                console.warn('Analytics logging failed:', error);
            });
        } catch (error) {
            console.warn('Analytics error:', error);
        }
    }

    // Performance tracking
    trackPerformance() {
        if ('performance' in window) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    this.logAnalytics('performance', {
                        load_time: perfData.loadEventEnd - perfData.loadEventStart,
                        dom_content_loaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                        page_load_time: perfData.loadEventEnd - perfData.fetchStart
                    });
                }, 1000);
            });
        }
    }
}

// Initialize quiz when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const quiz = new QuizApp();
    quiz.trackPerformance();
    
    // Make quiz available globally for debugging
    if (window.location.hostname === 'localhost' || window.location.hostname.includes('dev')) {
        window.quiz = quiz;
    }
});

// Error handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    
    // Log critical errors
    if (window.quiz) {
        window.quiz.logAnalytics('javascript_error', {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno
        });
    }
});

// Handle visibility changes (user switches tabs)
document.addEventListener('visibilitychange', () => {
    if (window.quiz) {
        window.quiz.logAnalytics('visibility_change', {
            hidden: document.hidden,
            screen: window.quiz.getCurrentScreen()
        });
    }
});

// Handle beforeunload (user leaving page)
window.addEventListener('beforeunload', () => {
    if (window.quiz && window.quiz.getCurrentScreen() === 'quiz-screen') {
        window.quiz.logAnalytics('quiz_abandoned', {
            question_number: window.quiz.currentQuestionIndex + 1,
            answers_completed: Object.keys(window.quiz.answers).length
        });
    }
});