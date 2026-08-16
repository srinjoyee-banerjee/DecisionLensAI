document.addEventListener("DOMContentLoaded", () => {

    const analyzeBtn =
        document.getElementById("analyzeBtn");


    // =========================================================
    // RESULT PAGE
    // =========================================================

    if (!analyzeBtn) {

        loadResults();

        return;
    }


    // =========================================================
    // WORKSPACE ELEMENTS
    // =========================================================

    const input =
        document.getElementById("decisionInput");

    const btnText =
        document.getElementById("btnText");

    const errorBox =
        document.getElementById("errorBox");


    // =========================================================
    // ANALYZE BUTTON
    // =========================================================

    analyzeBtn.addEventListener(
        "click",
        async () => {

            const decision =
                input
                    ? input.value.trim()
                    : "";


            // -------------------------------------------------
            // VALIDATION
            // -------------------------------------------------

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


            if (decision.length < 5) {

                showError(
                    errorBox,
                    "Please provide a more detailed decision."
                );

                return;
            }


            hideError(errorBox);


            // -------------------------------------------------
            // LOADING
            // -------------------------------------------------

            setLoadingState(
                analyzeBtn,
                btnText,
                true
            );


            try {

                // -------------------------------------------------
                // API REQUEST
                // -------------------------------------------------

                const response =
                    await fetch(
                        "/api/analyze",
                        {

                            method: "POST",

                            headers: {

                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({
                                    decision:
                                        decision
                                })
                        }
                    );


                // -------------------------------------------------
                // RESPONSE
                // -------------------------------------------------

                const contentType =
                    response.headers.get(
                        "content-type"
                    ) || "";


                let data;


                if (
                    contentType.includes(
                        "application/json"
                    )
                ) {

                    data =
                        await response.json();

                } else {

                    const text =
                        await response.text();

                    throw new Error(
                        text ||
                        "The server returned an invalid response."
                    );

                }


                // -------------------------------------------------
                // BACKEND ERROR
                // -------------------------------------------------

                if (!response.ok) {

                    throw new Error(
                        data.error ||
                        data.message ||
                        "Analysis failed."
                    );

                }


                // -------------------------------------------------
                // VALIDATE
                // -------------------------------------------------

                if (
                    !data ||
                    typeof data !== "object"
                ) {

                    throw new Error(
                        "The AI returned an invalid analysis."
                    );

                }


                // -------------------------------------------------
                // SAVE RESULT
                // -------------------------------------------------

                localStorage.setItem(
                    "decisionLensResult",
                    JSON.stringify(data)
                );


                // -------------------------------------------------
                // GO TO RESULT PAGE
                // -------------------------------------------------

                window.location.href =
                    "/result.html";

            }


            catch (error) {

                console.error(
                    "DecisionLens analysis error:",
                    error
                );


                showError(
                    errorBox,
                    "Analysis failed: " +
                    (
                        error.message ||
                        "Please try again."
                    )
                );


                setLoadingState(
                    analyzeBtn,
                    btnText,
                    false
                );

            }

        }
    );

});


// =============================================================
// RESULT PAGE
// =============================================================

function loadResults() {

    const raw =
        localStorage.getItem(
            "decisionLensResult"
        );


    // ---------------------------------------------------------
    // NO RESULT
    // ---------------------------------------------------------

    if (!raw) {

        showNoResultState();

        return;
    }


    try {

        const data =
            JSON.parse(raw);


        // -----------------------------------------------------
        // BASIC DATA
        // -----------------------------------------------------

        const decisionText =
            document.getElementById(
                "decisionText"
            );


        const recommendation =
            document.getElementById(
                "recommendation"
            );


        const summary =
            document.getElementById(
                "summary"
            );


        const confidence =
            document.getElementById(
                "confidence"
            );


        // -----------------------------------------------------
        // DECISION
        // -----------------------------------------------------

        if (decisionText) {

            decisionText.textContent =
                data.decision ||
                "No decision provided.";

        }


        // -----------------------------------------------------
        // CONFIDENCE
        // -----------------------------------------------------

        if (confidence) {

            const confidenceValue =
                Number(
                    data.confidence
                );


            if (
                !Number.isNaN(
                    confidenceValue
                )
            ) {

                confidence.textContent =
                    Math.round(
                        confidenceValue
                    ) + "%";

            } else {

                confidence.textContent =
                    "—";

            }

        }


        // -----------------------------------------------------
        // RECOMMENDED OPTION
        // -----------------------------------------------------

        renderRecommendedOption(
            data
        );


        // -----------------------------------------------------
        // RECOMMENDATION
        // -----------------------------------------------------

        if (recommendation) {

            recommendation.innerHTML =
                formatRecommendation(
                    data.recommendation ||
                    "No recommendation available."
                );

        }


        // -----------------------------------------------------
        // SUMMARY
        // -----------------------------------------------------

        if (summary) {

            summary.textContent =
                data.summary ||
                "No summary available.";

        }


        // -----------------------------------------------------
        // OPTION COMPARISON
        // -----------------------------------------------------

        renderOptionComparison(
            data
        );


        // -----------------------------------------------------
        // ANALYSIS LISTS
        // -----------------------------------------------------

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


        // -----------------------------------------------------
        // EVIDENCE
        // -----------------------------------------------------

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


// =============================================================
// RECOMMENDED OPTION
// =============================================================

function renderRecommendedOption(data) {

    const optionElement =
        document.getElementById(
            "recommendedOption"
        );


    const scoreElement =
        document.getElementById(
            "winnerScore"
        );


    const winner =
        data.recommended_option;


    const scores =
        data.option_scores || {};


    if (optionElement) {

        optionElement.textContent =
            winner ||
            "Decision requires further analysis.";

    }


    if (scoreElement) {

        if (
            winner &&
            scores[winner] !== undefined
        ) {

            scoreElement.textContent =
                Math.round(
                    Number(
                        scores[winner]
                    )
                );

        } else {

            scoreElement.textContent =
                "—";

        }

    }

}


// =============================================================
// OPTION COMPARISON
// =============================================================

function renderOptionComparison(data) {

    const container =
        document.getElementById(
            "optionComparison"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    const scores =
        data.option_scores || {};


    const options =
        Array.isArray(data.options)
            ? data.options
            : Object.keys(scores);


    if (!options.length) {

        container.innerHTML = `
            <div class="comparison-empty">
                No direct option comparison was detected.
            </div>
        `;

        return;
    }


    const winner =
        data.recommended_option;


    options.forEach(
        (option, index) => {

            const score =
                Number(
                    scores[option]
                );


            const safeScore =
                Number.isNaN(score)
                    ? 0
                    : Math.max(
                        0,
                        Math.min(
                            100,
                            score
                        )
                    );


            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "option-card";


            if (
                option === winner
            ) {

                card.classList.add(
                    "winner"
                );

            }


            const badge =
                option === winner
                    ? `<span class="winner-badge">
                            RECOMMENDED
                       </span>`
                    : `<span class="option-badge">
                            OPTION ${index + 1}
                       </span>`;


            card.innerHTML = `

                <div class="option-card-top">

                    <div>

                        ${badge}

                        <h3>
                            ${escapeHTML(option)}
                        </h3>

                    </div>

                    <div class="option-score">

                        <strong>
                            ${Math.round(safeScore)}
                        </strong>

                        <span>
                            /100
                        </span>

                    </div>

                </div>


                <div class="score-track">

                    <div
                        class="score-fill"
                        style="width:${safeScore}%"
                    ></div>

                </div>

            `;


            container.appendChild(
                card
            );

        }
    );

}


// =============================================================
// RECOMMENDATION FORMATTER
// =============================================================

function formatRecommendation(text) {

    if (!text) {
        return "";
    }


    let safe =
        escapeHTML(text);


    // Highlight option names marked with **
    safe =
        safe.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    return safe;

}


// =============================================================
// RENDER LIST
// =============================================================

function renderList(
    id,
    items
) {

    const element =
        document.getElementById(
            id
        );


    if (!element) {
        return;
    }


    element.innerHTML = "";


    if (!Array.isArray(items)) {
        items = [];
    }


    if (items.length === 0) {

        const li =
            document.createElement(
                "li"
            );


        li.textContent =
            "No major items identified.";


        element.appendChild(
            li
        );


        return;
    }


    items.forEach(
        item => {

            const li =
                document.createElement(
                    "li"
                );


            if (
                typeof item === "object" &&
                item !== null
            ) {

                li.textContent =
                    item.text ||
                    item.title ||
                    item.description ||
                    JSON.stringify(item);

            } else {

                li.textContent =
                    String(item);

            }


            element.appendChild(
                li
            );

        }
    );

}


// =============================================================
// RENDER EVIDENCE
// =============================================================

function renderEvidence(items) {

    const container =
        document.getElementById(
            "evidenceList"
        );


    const status =
        document.getElementById(
            "evidenceStatus"
        );


    const count =
        document.getElementById(
            "evidenceCount"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (!Array.isArray(items)) {
        items = [];
    }


    // ---------------------------------------------------------
    // COUNT
    // ---------------------------------------------------------

    if (count) {

        count.textContent =
            items.length +
            (
                items.length === 1
                    ? " SOURCE"
                    : " SOURCES"
            );

    }


    // ---------------------------------------------------------
    // NO EVIDENCE
    // ---------------------------------------------------------

    if (items.length === 0) {

        if (status) {

            status.textContent =
                "No directly matching knowledge-base evidence was retrieved.";

        }


        const div =
            document.createElement(
                "div"
            );


        div.className =
            "evidence-item empty";


        div.innerHTML = `

            <strong>
                Decision knowledge base
            </strong>

            <p>
                The recommendation was generated using
                DecisionLens' decision-analysis framework.
                No directly matching knowledge-base records
                were found for this decision.
            </p>

        `;


        container.appendChild(
            div
        );


        return;
    }


    // ---------------------------------------------------------
    // EVIDENCE FOUND
    // ---------------------------------------------------------

    if (status) {

        status.textContent =
            "Relevant knowledge-base intelligence was retrieved and considered.";

    }


    items.forEach(
        (item, index) => {

            const div =
                document.createElement(
                    "div"
                );


            div.className =
                "evidence-item";


            const title =
                item &&
                typeof item === "object"
                    ? item.title ||
                      item.source ||
                      "Retrieved intelligence"
                    : "Retrieved intelligence";


            const content =
                item &&
                typeof item === "object"
                    ? item.content ||
                      item.text ||
                      item.description ||
                      ""
                    : String(item);


            const relevance =
                item &&
                typeof item === "object" &&
                item.relevance !== undefined
                    ? Number(
                        item.relevance
                    )
                    : null;


            const terms =
                item &&
                typeof item === "object" &&
                Array.isArray(
                    item.matched_terms
                )
                    ? item.matched_terms
                    : [];


            let relevanceHTML =
                "";


            if (
                relevance !== null &&
                !Number.isNaN(relevance)
            ) {

                relevanceHTML = `

                    <span class="evidence-relevance">
                        ${Math.round(relevance)}% MATCH
                    </span>

                `;

            }


            let termsHTML =
                "";


            if (terms.length) {

                termsHTML = `

                    <div class="matched-terms">

                        ${terms
                            .slice(0, 6)
                            .map(
                                term =>
                                    `<span>
                                        ${escapeHTML(term)}
                                     </span>`
                            )
                            .join("")
                        }

                    </div>

                `;

            }


            div.innerHTML = `

                <div class="evidence-top">

                    <div class="evidence-index">
                        ${String(index + 1).padStart(2, "0")}
                    </div>

                    <div class="evidence-title">
                        <strong>
                            ${escapeHTML(title)}
                        </strong>
                    </div>

                    ${relevanceHTML}

                </div>


                <p>
                    ${escapeHTML(content)}
                </p>


                ${termsHTML}

            `;


            container.appendChild(
                div
            );

        }
    );

}


// =============================================================
// HTML ESCAPE
// =============================================================

function escapeHTML(text) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        text == null
            ? ""
            : String(text);


    return div.innerHTML;

}


// =============================================================
// LOADING STATE
// =============================================================

function setLoadingState(
    button,
    buttonText,
    loading
) {

    if (!button) {
        return;
    }


    if (loading) {

        button.classList.add(
            "loading"
        );


        button.disabled =
            true;


        if (buttonText) {

            buttonText.textContent =
                "AI ANALYZING";

        }

    }

    else {

        button.classList.remove(
            "loading"
        );


        button.disabled =
            false;


        if (buttonText) {

            buttonText.textContent =
                "ANALYZE DECISION";

        }

    }

}


// =============================================================
// ERROR DISPLAY
// =============================================================

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


// =============================================================
// HIDE ERROR
// =============================================================

function hideError(
    errorBox
) {

    if (!errorBox) {
        return;
    }


    errorBox.style.display =
        "none";


    errorBox.textContent =
        "";

}


// =============================================================
// NO RESULT STATE
// =============================================================

function showNoResultState() {

    const decisionText =
        document.getElementById(
            "decisionText"
        );


    const recommendedOption =
        document.getElementById(
            "recommendedOption"
        );


    const recommendation =
        document.getElementById(
            "recommendation"
        );


    const summary =
        document.getElementById(
            "summary"
        );


    const confidence =
        document.getElementById(
            "confidence"
        );


    if (decisionText) {

        decisionText.textContent =
            "No decision has been analyzed.";

    }


    if (recommendedOption) {

        recommendedOption.textContent =
            "No analysis available";

    }


    if (recommendation) {

        recommendation.textContent =
            "Start a new decision analysis to generate a recommendation.";

    }


    if (summary) {

        summary.textContent =
            "Return to the workspace and enter a decision with two options to receive a comparative DecisionLens report.";

    }


    if (confidence) {

        confidence.textContent =
            "—";

    }


    renderOptionComparison({
        options: [],
        option_scores: {}
    });


    renderEvidence([]);

}


// =============================================================
// RESULT ERROR STATE
// =============================================================

function showResultError() {

    const recommendation =
        document.getElementById(
            "recommendation"
        );


    const summary =
        document.getElementById(
            "summary"
        );


    if (recommendation) {

        recommendation.textContent =
            "Unable to load analysis.";

    }


    if (summary) {

        summary.textContent =
            "The saved DecisionLens result could not be read. Please return to Workspace and run the analysis again.";

    }

}
