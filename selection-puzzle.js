import {html, css, LitElement} from "https://unpkg.com/lit-element/lit-element.js?module"

class SelectionPuzzle extends LitElement {

    static properties = {
        question: String,
        answer: String,
        options: {
            type: Array,
            converter: (value, type) => {
                return value.split('').map(text => ({
                    text,
                    disabled: false,
                }));
            },
        },
        chosen: {
            type: String,
            reflect: true,
            converter: {
                fromAttribute: (value, type) => {
                    return value.split('');
                },
                toAttribute: (value, type) => {
                    return value.join('');
                }
            },
        },
    }

    constructor() {
        super();
        this.question = '';
        this.chosen = [];
    }

    choose(option) {
        option.disabled = true;
        this.chosen = [...this.chosen, option];
        option.found = this.answer.includes(option.text);
        option.correct = this.answer.indexOf(option.text) == (this.chosen.indexOf(option) % 4)
    }
    remove(option) {
        option.disabled = false;
        this.chosen.splice(this.chosen.indexOf(option), 1);
        this.chosen = [...this.chosen];
    }
    static styles = css`
        #options, #chosen {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-column-gap: 0.5em;
            grid-row-gap: 0.5em;
            width: min-content;
            margin: 1em;
        }
        .option {
            // width: 1em;
        }
        .option[found] {
            background: yellow;
        }
        .option[correct] {
            background: green;
        }
    `;

    render() {
        const { answer, options, chosen, question } = this;
        return html`
            <p>${question}</p>
            <p>${answer}</p>
            <div id="options">
            ${options.map(option => {
                const { text, disabled } = option;
                return html`<button ?disabled=${disabled} class="option" type="button" @click=${() => this.choose(option)}>${text}</button>`
            })}
            </div>
            <div id="chosen">
            ${chosen.map((option, index) => {
                if (Math.floor(index/4) == Math.floor(chosen.length/4)) {
                    return html`<button class="option" type="button" @click=${() => this.remove(option)}>${option.text}</button>`
                } else {
                    return html`<button disabled ?found=${option.found} ?correct=${option.correct} class="option" type="button" @click=${() => this.remove(option)}>${option.text}</button>`
                }
            })}
            </div>

        `
    }
}

customElements.define('selection-puzzle', SelectionPuzzle);