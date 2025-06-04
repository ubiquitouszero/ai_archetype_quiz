// Enhanced Quiz Application with FastAPI Integration
class QuizApp {
    constructor() {
        this.currentPage = 'landing-page';
        this.currentQuestionIndex = 0;
        this.answers = {};
        this.results = null;
        this.startTime = null;
        this.quizData = null;
        
        this.initializeApp();
    }

    async initializeApp() {
        try {
            // Load quiz data from API
            const response = await fetch('/api/quiz/data');
            this.quizData = await response.json();
            
            this.initializeEventListeners();
            this.showPage('landing-page');
        } catch (error) {
            console.error('Failed to load quiz data:', error);
            this.showError('Failed to load quiz. Please refresh the page.');
        }
    }

    // Navigation
    showPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('page--active');
        });
        
        // Show target page
        const targetPage = document.getElementById(pageId);
        if (targetPage) {
            targetPage.classList.add('page--active');
            targetPage.classList.add('fade-in');
            this.currentPage = pageId;
        }
    }

    // Event Listeners
    initializeEventListeners() {
        // Navigation buttons
        document.getElementById('start-quiz-btn')?.addEventListener('click', () => this.startQuiz());
        document.getElementById('admin-nav-btn')?.addEventListener('click', () => this.redirectToAdmin());
        document.getElementById('retake-quiz-btn')?.addEventListener('click', () => this.retakeQuiz());
        document.getElementById('view-summary-btn')?.addEventListener('click', () => this.viewSummary());
        document.getElementById('share-results-btn')?.addEventListener('click', () => this.shareResults());
        
        // Quiz navigation
        document.getElementById('prev-btn')?.addEventListener('click', () => this.previousQuestion());
        document.getElementById('next-btn')?.addEventListener('click', () => this.nextQuestion());
    }

    // Quiz Logic
    startQuiz() {
        if (!this.quizData || !this.quizData.questions) {
            this.showError('Quiz data not loaded. Please refresh the page.');
            return;
        }

        this.currentQuestionIndex = 0;
        this.answers = {};
        this.startTime = new Date();
        this.showPage('quiz-page');
        this.renderQuestion();
    }

    renderQuestion() {
        const question = this.quizData.questions[this.currentQuestionIndex];
        const currentQuestionNum = this.currentQuestionIndex + 1;
        const totalQuestions = this.quizData.questions.length;
        
        // Update progress
        const progressPercent = (currentQuestionNum / totalQuestions) * 100;
        const progressFill = document.getElementById('progress-fill');
        if (progressFill) {
            progressFill.style.width = `${progressPercent}%`;
        }
        
        // Update question counter
        const currentQuestionEl = document.getElementById('current-question');
        const totalQuestionsEl = document.getElementById('total-questions');
        if (currentQuestionEl) currentQuestionEl.textContent = currentQuestionNum;
        if (totalQuestionsEl) totalQuestionsEl.textContent = totalQuestions;
        
        // Update question text
        const questionTextEl = document.getElementById('question-text');
        if (questionTextEl) {
            questionTextEl.textContent = question.question;
        }
        
        // Render answer options
        const answersContainer = document.getElementById('answer-options');
        if (answersContainer) {
            answersContainer.innerHTML = '';
            
            Object.entries(question.answers).forEach(([key, text]) => {
                const answerElement = document.createElement('div');
                answerElement.className = 'answer-option';
                answerElement.innerHTML = `
                    <span class="answer-option__label">${key}.</span>
                    ${text}
                `;
                
                answerElement.addEventListener('click', () => this.selectAnswer(key, answerElement));
                answersContainer.appendChild(answerElement);
            });
        }
        
        // Update navigation buttons
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        
        if (prevBtn) prevBtn.disabled = this.currentQuestionIndex === 0;
        if (nextBtn) nextBtn.disabled = !this.answers[question.id];
        
        // Update next button text
        if (nextBtn) {
            nextBtn.textContent = this.currentQuestionIndex === totalQuestions - 1 ? 'Finish Quiz' : 'Next';
        }
        
        // Restore selected answer if it exists
        const savedAnswer = this.answers[question.id];
        if (savedAnswer && answersContainer) {
            const selectedOption = Array.from(answersContainer.children).find(
                option => option.textContent.startsWith(savedAnswer)
            );
            if (selectedOption) {
                selectedOption.classList.add('answer-option--selected');
            }
        }
    }

    selectAnswer(answerKey, element) {
        // Remove previous selection
        document.querySelectorAll('.answer-option').forEach(option => {
            option.classList.remove('answer-option--selected');
        });
        
        // Add selection to clicked element
        element.classList.add('answer-option--selected');
        
        // Save answer
        const questionId = this.quizData.questions[this.currentQuestionIndex].id;
        this.answers[questionId] = answerKey;
        
        // Enable next button
        const nextBtn = document.getElementById('next-btn');
        if (nextBtn) nextBtn.disabled = false;
    }

    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.renderQuestion();
        }
    }

    nextQuestion() {
        if (this.currentQuestionIndex < this.quizData.questions.length - 1) {
            this.currentQuestionIndex++;
            this.renderQuestion();
        } else {
            this.finishQuiz();
        }
    }

    async finishQuiz() {
        try {
            this.showLoading('Calculating your archetype...');
            
            const endTime = new Date();
            const completionTime = (endTime - this.startTime) / 1000 / 60; // minutes
            
            const response = await fetch('/api/quiz/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    responses: this.answers,
                    completion_time: completionTime
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.results = await response.json();
            this.hideLoading();
            this.showPage('results-page');
            this.renderResults();
            
        } catch (error) {
            this.hideLoading();
            console.error('Error submitting quiz:', error);
            this.showError('Failed to submit quiz. Please try again.');
        }
    }

    renderResults() {
        if (!this.results) return;

        const { primary_archetype, scores, archetype_data, session_id } = this.results;

        // Update primary archetype display
        const nameEl = document.getElementById('primary-archetype-name');
        const scoreEl = document.getElementById('primary-archetype-score');
        const descEl = document.getElementById('primary-archetype-description');
        const approachEl = document.getElementById('primary-archetype-approach');

        if (nameEl) nameEl.textContent = primary_archetype;
        if (scoreEl) scoreEl.textContent = `${scores[primary_archetype]}%`;
        if (descEl) descEl.textContent = archetype_data.description || '';
        if (approachEl) approachEl.textContent = archetype_data.approach || '';

        // Update characteristics list
        const characteristicsList = document.getElementById('primary-archetype-characteristics');
        if (characteristicsList && archetype_data.characteristics) {
            characteristicsList.innerHTML = '';
            archetype_data.characteristics.forEach(characteristic => {
                const li = document.createElement('li');
                li.textContent = characteristic;
                characteristicsList.appendChild(li);
            });
        }

        // Update score breakdown
        const scoreBreakdown = document.getElementById('score-breakdown');
        if (scoreBreakdown) {
            scoreBreakdown.innerHTML = '';
            
            // Sort scores by value for better display
            const sortedScores = Object.entries(scores).sort(([,a], [,b]) => b - a);
            
            sortedScores.forEach(([archetype, score]) => {
                const scoreItem = document.createElement('div');
                scoreItem.className = 'score-item';
                const archetypeData = this.quizData.archetypes[archetype] || {};
                scoreItem.innerHTML = `
                    <div class="score-item__archetype">
                        <span class="score-item__icon">${archetypeData.icon || '📊'}</span>
                        <span class="score-item__name">${archetype}</span>
                    </div>
                    <span class="score-item__value">${score}%</span>
                `;
                scoreBreakdown.appendChild(scoreItem);
            });
        }

        // Store session ID for sharing
        this.sessionId = session_id;
        
        // Update share button with results URL
        this.updateShareButton();
    }

    updateShareButton() {
        const shareBtn = document.getElementById('share-results-btn');
        if (shareBtn && this.sessionId) {
            shareBtn.style.display = 'inline-flex';
        }
    }

    shareResults() {
        if (!this.sessionId) return;

        const resultsUrl = `${window.location.origin}/results/${this.sessionId}`;
        const shareText = `I just discovered my AI workplace archetype: ${this.results.primary_archetype}! Find out yours:`;
        
        if (navigator.share) {
            navigator.share({
                title: 'My AI Archetype Results',
                text: shareText,
                url: resultsUrl
            }).catch(console.error);
        } else {
            // Fallback to clipboard
            navigator.clipboard.writeText(`${shareText} ${resultsUrl}`).then(() => {
                this.showNotification('Results URL copied to clipboard!');
            }).catch(() => {
                // Final fallback - show URL
                prompt('Share this URL:', resultsUrl);
            });
        }
    }

    retakeQuiz() {
        this.startQuiz();
    }

    redirectToAdmin() {
        window.location.href = '/admin/login';
    }

    viewSummary() {
        window.location.href = '/summary';
    }

    // Utility methods
    showLoading(message = 'Loading...') {
        const loadingEl = document.getElementById('loading-overlay');
        if (loadingEl) {
            loadingEl.querySelector('.loading-text').textContent = message;
            loadingEl.style.display = 'flex';
        }
    }

    hideLoading() {
        const loadingEl = document.getElementById('loading-overlay');
        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
    }

    showError(message) {
        const errorEl = document.getElementById('error-message');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.style.display = 'block';
            setTimeout(() => {
                errorEl.style.display = 'none';
            }, 5000);
        } else {
            alert(message);
        }
    }

    showNotification(message) {
        const notificationEl = document.getElementById('notification');
        if (notificationEl) {
            notificationEl.textContent = message;
            notificationEl.classList.add('show');
            setTimeout(() => {
                notificationEl.classList.remove('show');
            }, 3000);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new QuizApp();
});

// Admin Dashboard functionality (if on admin page)
if (window.location.pathname.includes('/admin')) {
    class AdminDashboard {
        constructor() {
            this.initializeAdmin();
        }

        async initializeAdmin() {
            await this.loadStats();
            this.setupAutoRefresh();
        }

        async loadStats() {
            try {
                const response = await fetch('/api/admin/stats');
                if (!response.ok) {
                    if (response.status === 401) {
                        window.location.href = '/admin/login';
                        return;
                    }
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                this.renderStats(data);
                this.renderArchetypeChart(data);
                this.renderRecentSubmissions(data);
            } catch (error) {
                console.error('Failed to load admin stats:', error);
            }
        }

        renderStats(data) {
            // Update summary stats
            const elements = {
                'total-submissions': data.total_submissions,
                'completion-rate': '92%', // Calculate from data if needed
                'average-time': `${data.average_completion_time} min`,
                'most-common-type': Object.keys(data.archetype_distribution)[0] || 'N/A'
            };

            Object.entries(elements).forEach(([id, value]) => {
                const el = document.getElementById(id);
                if (el) el.textContent = value;
            });
        }

        renderArchetypeChart(data) {
            const chartContainer = document.getElementById('archetype-chart');
            if (!chartContainer || !data.archetype_distribution) return;

            // Simple bar chart using CSS
            chartContainer.innerHTML = '';
            
            const total = Object.values(data.archetype_distribution).reduce((sum, count) => sum + count, 0);
            
            Object.entries(data.archetype_distribution).forEach(([archetype, count]) => {
                const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                const archetypeData = data.archetype_data[archetype] || {};
                
                const bar = document.createElement('div');
                bar.className = 'chart-bar';
                bar.innerHTML = `
                    <div class="chart-bar__label">
                        <span class="chart-bar__icon">${archetypeData.icon || '📊'}</span>
                        ${archetype}
                    </div>
                    <div class="chart-bar__value">
                        <div class="chart-bar__fill" style="width: ${percentage}%; background-color: ${archetypeData.color || '#4ECDC4'}"></div>
                        <span class="chart-bar__percentage">${percentage}%</span>
                    </div>
                `;
                chartContainer.appendChild(bar);
            });
        }

        renderRecentSubmissions(data) {
            const container = document.getElementById('recent-submissions-list');
            if (!container || !data.recent_submissions) return;

            container.innerHTML = '';

            data.recent_submissions.slice(0, 10).forEach(submission => {
                const row = document.createElement('div');
                row.className = 'table-row';
                
                const date = new Date(submission.completed_at);
                const formattedDate = date.toLocaleDateString();
                const formattedTime = date.toLocaleTimeString();
                
                row.innerHTML = `
                    <div>${formattedDate} ${formattedTime}</div>
                    <div>
                        <span class="archetype-badge" style="background-color: ${data.archetype_data[submission.archetype]?.color || '#4ECDC4'}">
                            ${submission.archetype}
                        </span>
                    </div>
                    <div>${submission.completion_time || 'N/A'} min</div>
                    <div>
                        <a href="/results/${submission.session_id}" target="_blank" class="view-link">View</a>
                    </div>
                `;
                container.appendChild(row);
            });
        }

        setupAutoRefresh() {
            // Refresh stats every 30 seconds
            setInterval(() => this.loadStats(), 30000);
        }
    }

    // Initialize admin dashboard
    new AdminDashboard();
}
