const USE_MOCK = true;

// Mock Data
const MOCK_FINDINGS = [
    {
        finding_id: "f1",
        rule_id: "aws-access-key",
        file_path: "src/config/aws.js",
        secret_snippet: "const AWS_KEY = 'aws-test-key';",
        is_false_positive: true,
        confidence: 0.95,
        ai_verdict: "Test data: contains 'EXAMPLE' keyword commonly used in documentation."
    },
    {
        finding_id: "f2",
        rule_id: "slack-bot-token",
        file_path: "backend/services/slack.py",
        secret_snippet: "bot_token = 'bot-token';",
        is_false_positive: false,
        confidence: 0.99,
        ai_verdict: "High entropy string matching Slack token pattern. Likely valid."
    },
    {
        finding_id: "f3",
        rule_id: "generic-api-key",
        file_path: "tests/fixtures/mock_data.json",
        secret_snippet: "\"api_key\": \"api-key\"",
        is_false_positive: true,
        confidence: 0.60,
        ai_verdict: "Located in 'tests' directory. Likely test credential."
    }
];

const api = {
    // --- Auth ---
    async login(username, password) {
        if (USE_MOCK) {
            return new Promise((resolve, reject) => {
                setTimeout(() => {
                    if (password.length < 8) {
                        reject({ message: "Password must be at least 8 characters" });
                    } else if (username === "fail") {
                        reject({ message: "Invalid credentials" });
                    } else {
                        resolve({
                            access_token: "mock_jwt_token_" + Date.now(),
                            user: { id: "u1", username: username, firstname: "Admin", email: `${username}@example.com` }
                        });
                    }
                }, 800);
            });
        }
        // Real fetch implementation
    },

    async register(username, email, password, firstname, lastname) {
        if (USE_MOCK) {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve({
                        user: { id: "u2", username, email, firstname, lastname },
                        message: "User created"
                    });
                }, 800);
            });
        }
    },

    async logout() {
        if (USE_MOCK) {
            return Promise.resolve();
        }
    },

    // --- Analysis ---
    async analyze(file, tool) {
        if (USE_MOCK) {
            return new Promise(resolve => setTimeout(() => {
                resolve({ report_id: "rpt_" + Date.now().toString().slice(-6), status: "processing" });
            }, 800));
        }
    },

    async getResults(reportId) {
        if (USE_MOCK) {
            return new Promise(resolve => setTimeout(() => {
                resolve({
                    report_id: reportId,
                    status: "completed",
                    findings: MOCK_FINDINGS,
                    stats: { total_findings: 3, filtered_fp: 2, remaining_tp: 1 },
                    created_at: new Date().toISOString()
                });
            }, 1500));
        }
    },

    async sendFeedback(reportId, findingId, label) {
        if (USE_MOCK) {
            console.log(`Feedback: ${reportId} / ${findingId} -> ${label}`);
            return Promise.resolve({ success: true });
        }
    }
};

window.api = api; // Expose globally
