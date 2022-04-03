import {html, css, LitElement} from "https://unpkg.com/lit-element/lit-element.js?module"

function getIndexes(char, string) {
    const indexes = [];
    for (let i = 0; i < string.length; i++) {
        if (string[i] === char) indexes.push(i)
    }
    return indexes;
}

export default class SelectionPuzzle extends LitElement {

    static properties = {
        complete: Boolean,
        question: String,
        answer: String,
        disableIncorrect: {
            type: Boolean,
            attribute: 'disable-incorrect',
        },
        options: {
            type: Array,
            converter: (value, type) => {
                return value.split('').map(text => ({
                    text,
                    disabled: false,
                }));
            },
        },
        attempts: Array,
        attempt: Object,
    }

    constructor() {
        super();
        this.question = '';
        this.complete = false;
        this.attempt = { options: [] };
        this.attempts = [this.attempt];
    }

    check(attempt, answer) {
        attempt.options.forEach(option => option.disabled = false);
        attempt.found = attempt.options.map(option => answer.includes(option.text))
        attempt.correct = attempt.options.map((option, index) => {
            return getIndexes(option.text, answer).includes(index);
        })
        attempt.checked = true;
        return attempt.options.map(option => option.text).join('') == answer;
    }

    choose(option) {
        option.disabled = true;
        const attempt = this.attempt;
        attempt.options.push(option);

        // If this attempt should be checked
        if (attempt.options.length == 4) {
            this.correct = this.check(attempt, this.answer);

            // Hide disable options that were selected but not found
            this.disableIncorrect &&
                this.attempt.options
                    .forEach((option, i) => option.disabled = !this.attempt.found[i])

            // If 4 attempts have been made, end the puzzle
            if (this.attempts.length == 4) {
                this.options.forEach(option => option.disabled = true);
                this.complete = true;
            }

            // Start a new attempt
            this.attempt = { options: [] };
            this.attempts.push(this.attempt);
        }

        // Update the gui
        this.requestUpdate();
    }
    remove(option) {
        option.disabled = false;
        this.attempt.options.splice(this.attempt.options.indexOf(option), 1);
        this.requestUpdate();
    }
    static styles = css`
        #options, #attempts {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-column-gap: 0.5em;
            grid-row-gap: 0.5em;
            width: min-content;
            margin: 1em;
        }
        .option {
            width: 70px;
            height: max-content;
        }
        .option[found] {
            background: yellow;
        }
        .option[correct] {
            background: green;
        }
    `;


    render() {
        const { answer, options, question, attempts, attempt } = this;
        console.log({
            attempts, attempt
        })
        return html`
            <p>${question}</p>
            <div id="options">
            ${options.map(option => {
                const { text, disabled } = option;
                return html`<button ?disabled=${disabled} class="option" type="button" @click=${() => this.choose(option)}>${text}</button>`
            })}
            </div>
            <div id="attempts">
            ${attempts.filter(attempt => attempt.checked).map((attempt) => {
                return attempt.options.map((option, i) => {
                    return html`<button disabled ?found=${attempt.found[i]} ?correct=${attempt.correct[i]} class="option" type="button" @click=${() => this.remove(option)}>${option.text}</button>`
                })
            })}
            ${attempt.options.map(option => {
                return html`<button class="option" type="button" @click=${() => this.remove(option)}>${option.text}</button>`
            })}
            </div>
            ${this.correct ? html`<p>Nice work</p>` : ''}
        `
    }
}

customElements.define('selection-puzzle', SelectionPuzzle);