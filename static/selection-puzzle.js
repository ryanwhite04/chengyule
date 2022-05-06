// check('abcd')('x', 1) == 0 // not found
// check('abcd')('a', 1) == 1 // found but not correct
// check('abcd')('b', 1) == 2 // correct
function check(string) {
    return (v, i) => string.includes(v) ? string[i] == v ? 2 : 1 : 0;
}

export default class SelectionPuzzle extends HTMLElement {

    static get observedAttributes() {
        return ["answer", "disable-incorrect"]
    }

    get styles() {
        const tag = document.createElement('style');
        tag.textContent = `
            :host {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .grid {
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
        return tag;
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name == "disable-incorrect") {
            this.disableIncorrect = newValue !== null;
        } else {
            this[name] = newValue;
        }
    }

    state = "playing";
    attempt = {
        options: [],
        choices: [],
    };
    disableIncorrect = false;

    constructor() {
        super();
        this.attempts = [this.attempt];
        this.attachShadow({ mode: "open" });
        this.shadowRoot.appendChild(this.styles);
        this.render(this.shadowRoot);
    }

    submit(attempt) {
        attempt.value = attempt.options
            .map(option => option.textContent) // get the value of each option
            .map(check(this.answer)) // check if the value is found or correct in the answer

        attempt.choices.forEach((choice, i) => {
            choice.disabled = true;
            attempt.value[i] == 1 && choice.setAttribute("found", "");
            attempt.value[i] == 2 && choice.setAttribute("correct", "");
        });
        attempt.options.forEach((option, i) => {
            option.disabled = this.disableIncorrect && !attempt.value[i]
        })
        return attempt.value.every(v => v == 2)
    }

    // End the game
    finish(success) {
        this[success ? "success" : "failure"].removeAttribute('hidden');
        this.options // the slot that the options are in
            .assignedElements() // the options in the light dom
            .forEach(option => option.disabled = true); // disable them all to end game
        this.dispatchEvent(new CustomEvent('complete', {
            detail: success
        }))
    }

    select(event) {
        const { target: option } = event
        if (option.slot === 'option') {
            option.disabled = true;
            this.attempt.options.push(option);
            this.choose(option, this.attempt);
            if (this.attempt.options.length == 4) {
                if (this.submit(this.attempt)) this.finish(true);
                else if (this.attempts.length == 4) this.finish(false);
                else this.attempts.push(this.attempt = {
                    options: [],
                    choices: [],
                });
            }
        }
    }

    render() {
        const slot = document.createElement('slot');

        this.options = document.createElement('slot');
        this.options.setAttribute('name', 'option');
        this.options.addEventListener('click', this.select.bind(this));
        this.options.classList.add("grid");

        this.choices = document.createElement('div');
        this.choices.classList.add("grid");

        this.success = document.createElement('slot');
        this.success.setAttribute("name", "success");
        this.success.textContent = "Success";
        this.success.setAttribute("hidden", "");

        this.failure = document.createElement('slot');
        this.failure.setAttribute("name", "failure");
        this.failure.textContent = "Failure";
        this.failure.setAttribute("hidden", "");

        this.shadowRoot.append(
            slot,
            this.options,
            this.choices,
            this.success,
            this.failure
        );
    }

    choose(option, attempt) {
        const choice = document.createElement("button");
        choice.classList.add("choice");
        choice.setAttribute("part", "choice");
        choice.textContent = option.textContent;
        const remove = () => {
            option.disabled = false;
            attempt.options.splice(attempt.options.indexOf(option), 1);
            this.choices.removeChild(choice);
            attempt.choices.splice(attempt.choices.indexOf(choice), 1);
        }
        choice.addEventListener("click", remove)
        attempt.choices.push(choice);
        this.choices.append(choice);
    }
}

customElements.define('selection-puzzle', SelectionPuzzle);