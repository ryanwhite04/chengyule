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

    submit(attempt) {
        attempt.options.forEach(option => option.disabled = false);
        attempt.found = attempt.options.map(option => this.answer.includes(option.textContent))
        attempt.correct = attempt.options.map((option, index) => getIndexes(option.textContent, this.answer).includes(index))
        attempt.checked = true;

        // Hide disable options that were selected but not found
        this.disableIncorrect &&
            this.attempt.options
                .forEach((option, i) => option.disabled = !this.attempt.found[i])

        // If 4 attempts have been made, end the puzzle
        if (this.attempts.length == 4) {
            this.shadowRoot.getElementById('options').assignedElements().forEach(option => option.disabled = true)
            this.complete = true;
        }

        // Start a new attempt
        this.attempt = { options: [] };
        this.attempts.push(this.attempt);
        this.correct = attempt.options.map(option => option.text).join('') == this.answer;
    }

    choose(event) {
        const { target: option } = event
        if (option.slot === 'option') {
            option.disabled = true;
            this.attempt.options.push(option);
    
            // If this attempt should be checked
            if (this.attempt.options.length == 4) this.submit(this.attempt);
    
            // Update the gui
            this.requestUpdate();
        }
    }

    remove(option) {
        option.disabled = false;
        this.attempt.options.splice(this.attempt.options.indexOf(option), 1);
        this.requestUpdate();
    }

    static styles = css`
        :host {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        #options, #attempts {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-column-gap: 0.5em;
            grid-row-gap: 0.5em;
            margin: 1em;
        }
        .option {
            height: 3em;
            width: 3em;
        }
        .option[found] {
            background: yellow;
            color: black;
        }
        .option[correct] {
            background: green;
            color: black;
        }
        ::slotted([slot="option"]) {
            height: 3em;
            width: 3em;
            text-align: center;
        }
    `;

    render() {
        const { attempts, attempt } = this;
        return html`
            <slot></slot>
            <slot id="options" @click=${this.choose} name="option"></slot>
            <div id="attempts">
            ${attempts.filter(attempt => attempt.checked).map((attempt) => {
                return attempt.options.map((option, i) => {
                    return html`<button disabled ?found=${attempt.found[i]} ?correct=${attempt.correct[i]} class="option" type="button" @click=${() => this.remove(option)}>${option.textContent}</button>`
                })
            })}
            ${attempt.options.map(option => {
                return html`<button class="option" @click=${() => this.remove(option)}>${option.textContent}</button>`
            })}
            </div>
        `
    }
}

customElements.define('selection-puzzle', SelectionPuzzle);