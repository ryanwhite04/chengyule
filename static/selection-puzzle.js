import {html, css, LitElement} from "https://unpkg.com/lit-element/lit-element.js?module"

// check('abcd')('x', 1) == 0 // not found
// check('abcd')('a', 1) == 1 // found but not correct
// check('abcd')('b', 1) == 2 // correct
function check(string) {
    return (v, i) => string.includes(v) ? string[i] == v ? 2 : 1 : 0;
}

export default class SelectionPuzzle extends LitElement {

    static properties = {
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
        this.attempt = { options: [] };
        this.attempts = [this.attempt];
    }

    submit(attempt) {
        attempt.value = attempt.options
            .map(option => option.textContent) // get the value of each option
            .map(check(this.answer)) // check if the value is found or correct in the answer

        // Hide disable options that were selected but not found
        this.disableIncorrect &&  // only if the disableIncorrect option is set
            attempt.options.forEach((option, i) => option.disabled = !attempt.value[i])

        this.attempt = { options: [] };
        this.attempts.push(this.attempt);

        return attempt.value.every(v => v == 2) // word is correct
            || this.attempts.length > 4 // or no attempts left
    }

    // End the game
    finish(success) {
        this.shadowRoot
            .getElementById('options') // the slot that the options are in
            .assignedElements() // the options in the light dom
            .forEach(option => option.disabled = true); // disable them all to end game
        this.dispatchEvent(new CustomEvent('complete', {
            detail: success
        }))
    }

    choose(event) {
        const { target: option } = event
        if (option.slot === 'option') {
            option.disabled = true;
            this.attempt.options.push(option);
                this.attempt.options.length == 4 &&
                this.submit(this.attempt) &&
                this.finish();
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
        #options, #choices {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-column-gap: 0.5em;
            grid-row-gap: 0.5em;
            margin: 1em;
        }
        .choice {
            height: 3em;
            width: 3em;
            color: black;
        }
        .choice[found] {
            background: yellow;
        }
        .choice[correct] {
            background: green;
        }
        ::slotted([slot="option"]) {
            height: 3em;
            width: 3em;
            text-align: center;
        }
    `;

    render() {
        const choices = this.attempts
            .map(({ options, value }) => options.map(this.choice(value)));
        return html`
            <slot></slot>
            <slot id="options" @click=${this.choose} name="option"></slot>
            <div id="choices">${choices}</div>`
    }

    choice(value) {
        return (option, i) => value ? // if attempt has been submitted it will have a value
            html`<button class="choice" part="choice"
                disabled ?found=${value[i] == 1} ?correct=${value[i] == 2}
                >${option.textContent}</button>` :
            html`<button class="choice" part="choice"
                @click=${() => this.remove(option)}
                >${option.textContent}</button>`
    }
}

customElements.define('selection-puzzle', SelectionPuzzle);