document.addEventListener("DOMContentLoaded", () => {

    const analyzeBtn = document.getElementById("analyzeBtn");

    // ------------------------------------------------------------
    // RESULT PAGE
    // ------------------------------------------------------------

    if (!analyzeBtn) {
        loadResults();
        return;
    }


    // ------------------------------------------------------------
    // INDEX PAGE ELEMENTS
    // ------------------------------------------------------------

    const input = document.getElementById("decisionInput");
    const btnText = document.getElementById("btnText");
    const errorBox = document.getElementById("errorBox");


    // ------------------------------------------------------------
    // ANALYZE BUTTON
    // ------------------------------------------------------------

    analyzeBtn.addEventListener("click", async () => {

        const decision = input ? input.value.trim() : "";


        // Empty input
        if (!decision) {

            showError(
                errorBox,
                "Please describe the decision before starting the analysis."
            );

            if (input) {
                input.focus();
            }

            return;
        }


        hideError(errorBox);


        // Loading state
        setLoadingState(analyzeBtn, btnText, true);


        try {

            const response = await fetch("/api/analyze", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },

                body: JSON.stringify({
                    decision: decision
                })

            });


            // ----------------------------------------------------
            // SAFE RESPONSE PARSING
            // ----------------------------------------------------

            let data;

            const contentType =
                response.headers.get("content-type") || "";

            if (contentType.includes("application/json")) {

                data = await response.json();

            } else {

                const text = await response.text();

                throw new Error(
                    text || "The server returned an invalid response."
                );

            }


            // ----------------------------------------------------
            // BACKEND ERROR
            // ----------------------------------------------------

            if (!response.ok) {

                throw new Error(
                    data.error ||
                    data.message ||
                    "Analysis failed."
                );

            }


            // ----------------------------------------------------
            // VALIDATE RESULT
            // ----------------------------------------------------

            if (!data || typeof data !== "object") {

                throw new Error(
                    "The AI returned an invalid analysis."
                );

            }


            // ----------------------------------------------------
            // SAVE RESULT
            // ----------------------------------------------------

            localStorage.setItem(
                "decisionLensResult",
                JSON.stringify(data)
            );


            // ----------------------------------------------------
            // MOVE TO RESULT PAGE
            // ----------------------------------------------------

            window.location.href = "/result.html";

        }


        // --------------------------------------------------------
        // ERROR HANDLING
        // --------------------------------------------------------

        catch (error) {

            console.error(
                "DecisionLens analysis error:",
                error
            );


            showError(
                errorBox,
                "Analysis failed: " +
                (error.message || "Please try again.")
            );


            // Restore button
            setLoadingState(
                analyzeBtn,
                btnText,
                false
            );

        }

    });

});



// =================================================================
// RESULT PAGE
// =================================================================

function loadResults() {

    const raw =
        localStorage.getItem("decisionLensResult");


    // No saved result
    if (!raw) {

        showNoResultState();

        return;
    }


    try {

        const data =
            JSON.parse(raw);


        // ---------------------------------------------------------
        // BASIC RESULT INFORMATION
        // ---------------------------------------------------------

        const decisionText =
            document.getElementById("decisionText");

        const recommendation =
            document.getElementById("recommendation");

        const summary =
            document.getElementById("summary");

        const confidence =
            document.getElementById("confidence");


        if (decisionText) {

            decisionText.textContent =
                data.decision || "No decision provided.";

        }


        if (recommendation) {

            recommendation.textContent =
                data.recommendation ||
                "No recommendation available.";

        }


        if (summary) {

            summary.textContent =
                data.summary ||
                "No summary available.";

        }


        if (confidence) {

            const confidenceValue =
                Number(data.confidence);


            if (!Number.isNaN(confidenceValue)) {

                confidence.textContent =
                    Math.round(confidenceValue) + "%";

            } else {

                confidence.textContent =
                    "—";

            }

        }


        // ---------------------------------------------------------
        // INTELLIGENCE LISTS
        // ---------------------------------------------------------

        renderList(
            "factors",
            data.factors
        );


        renderList(
            "risks",
            data.risks
        );


        renderList(
            "opportunities",
            data.opportunities
        );


        renderList(
            "tradeoffs",
            data.tradeoffs
        );


        // ---------------------------------------------------------
        // EVIDENCE
        // ---------------------------------------------------------

        renderEvidence(
            data.evidence
        );

    }


    catch (error) {

        console.error(
            "Could not load DecisionLens result:",
            error
        );

        showResultError();

    }

}



// =================================================================
// RENDER LIST
// =================================================================

function renderList(id, items) {

    const element =
        document.getElementById(id);


    if (!element) {
        return;
    }


    element.innerHTML = "";


    // -------------------------------------------------------------
    // NORMALIZE DATA
    // -------------------------------------------------------------

    if (!Array.isArray(items)) {

        items = [];

    }


    // -------------------------------------------------------------
    // EMPTY LIST
    // -------------------------------------------------------------

    if (items.length === 0) {

        const li =
            document.createElement("li");

        li.textContent =
            "No major items identified.";

        element.appendChild(li);

        return;
    }


    // -------------------------------------------------------------
    // CREATE ITEMS
    // -------------------------------------------------------------

    items.forEach(item => {

        const li =
            document.createElement("li");


        if (typeof item === "object" && item !== null) {

            li.textContent =
                item.text ||
                item.title ||
                item.description ||
                JSON.stringify(item);

        } else {

            li.textContent =
                String(item);

        }


        element.appendChild(li);

    });

}



// =================================================================
// RENDER EVIDENCE
// =================================================================

function renderEvidence(items) {

    const container =
        document.getElementById("evidenceList");


    if (!container) {
        return;
    }


    container.innerHTML = "";


    // -------------------------------------------------------------
    // NORMALIZE DATA
    // -------------------------------------------------------------

    if (!Array.isArray(items)) {

        items = [];

    }


    // -------------------------------------------------------------
    // NO EVIDENCE
    // -------------------------------------------------------------

    if (items.length === 0) {

        const div =
            document.createElement("div");

        div.className =
            "evidence-item";


        div.innerHTML = `
            <strong>Decision knowledge base</strong>
            <p>
                No additional retrieved evidence was required
                for this analysis.
            </p>
        `;


        container.appendChild(div);

        return;
    }


    // -------------------------------------------------------------
    // EVIDENCE ITEMS
    // -------------------------------------------------------------

    items.forEach(item => {

        const div =
            document.createElement("div");


        div.className =
            "evidence-item";


        const title =
            item && typeof item === "object"
                ? item.title ||
                  item.source ||
                  "Retrieved intelligence"
                : "Retrieved intelligence";


        const content =
            item && typeof item === "object"
                ? item.content ||
                  item.text ||
                  item.description ||
                  ""
                : String(item);


        div.innerHTML = `
            <strong>
                ${escapeHTML(title)}
            </strong>

            <p>
                ${escapeHTML(content)}
            </p>
        `;


        container.appendChild(div);

    });

}



// =================================================================
// HTML ESCAPE
// =================================================================

function escapeHTML(text) {

    const div =
        document.createElement("div");


    div.textContent =
        text == null
            ? ""
            : String(text);


    return div.innerHTML;

}



// =================================================================
// LOADING STATE
// =================================================================

function setLoadingState(
    button,
    buttonText,
    loading
) {

    if (!button) {
        return;
    }


    if (loading) {

        button.classList.add("loading");

        button.disabled = true;


        if (buttonText) {

            buttonText.textContent =
                "AI ANALYZING";

        }

    } else {

        button.classList.remove("loading");

        button.disabled = false;


        if (buttonText) {

            buttonText.textContent =
                "ANALYZE DECISION";

        }

    }

}



// =================================================================
// ERROR DISPLAY
// =================================================================

function showError(
    errorBox,
    message
) {

    if (!errorBox) {
        return;
    }


    errorBox.style.display =
        "block";


    errorBox.textContent =
        message;

}



// =================================================================
// HIDE ERROR
// =================================================================

function hideError(errorBox) {

    if (!errorBox) {
        return;
    }


    errorBox.style.display =
        "none";


    errorBox.textContent =
        "";

}



// =================================================================
// NO RESULT STATE
// =================================================================

function showNoResultState() {

    const recommendation =
        document.getElementById("recommendation");

    const summary =
        document.getElementById("summary");

    const confidence =
        document.getElementById("confidence");


    if (recommendation) {

        recommendation.textContent =
            "No analysis available.";

    }


    if (summary) {

        summary.textContent =
            "Start a new decision analysis to generate your DecisionLens report.";

    }


    if (confidence) {

        confidence.textContent =
            "—";

    }

}



// =================================================================
// RESULT ERROR STATE
// =================================================================

function showResultError() {

    const recommendation =
        document.getElementById("recommendation");

    const summary =
        document.getElementById("summary");


    if (recommendation) {

        recommendation.textContent =
            "Unable to load analysis.";

    }


    if (summary) {

        summary.textContent =
            "The saved DecisionLens result could not be read. Please return and run the analysis again.";

    }

}
