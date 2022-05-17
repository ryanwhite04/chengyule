// check('abcd')('x', 1) == 0 // not found
// check('abcd')('a', 1) == 1 // found but not correct
// check('abcd')('b', 1) == 2 // correct
function check(string) {
    return (v, i) => string.includes(v) ? string[i] == v ? 2 : 1 : 0;
}

export default class SelectionPuzzle extends HTMLElement {

    _cache = new Cache();
    _tries = 4;
    state = "playing";
    attempt = {
        options: [],
        choices: [],
    };

    static get observedAttributes() {
        return Object.keys(this.converters);
    }

    attributeChangedCallback(name, _, value) {
        const converter = this.constructor.converters[name];
        // Called on window specifically to avoid illegal invocation
        this[name] = converter == Boolean ?
            this.hasAttribute(name) : // because Boolean("") returns false
            converter.call(window, value);
    }

    static converters = {
        "for": id => document.getElementById(id), // this input to submit guesses to
        "cache": String, // whether or not to save progress
        "tries": Number, // how many tries they get
        "answer": String, // the solution
        "guidance": Boolean, // whether or not to hide wrong choices

    }

    set cache(id) {
        this._cache = new Cache(id);
        this._replay = true;
        const options = this.options.assignedElements();
        for (let index of this._cache) {
            this.push(options[index])
        }
        this._replay = false;
    }

    get cache() {
        return this._cache;
    }

    set tries(value) {
        this.updateProgress(this.attempts.length, this._tries = value);
    }
    get tries() {
        return this._tries;
    }

    updateProgress(attempts, tries) {
        const remaining = tries-attempts;
        this.progress.textContent = `You have ${1+remaining} ${remaining ? "tries" : "try"} left`;
    }

    constructor() {
        super();
        this.attempts = [this.attempt];
        this.attachShadow({ mode: "open" });
        this.shadowRoot.appendChild(this.styles);
        this.render(this.shadowRoot);
    }

    connectedCallback() {
        this.updateProgress(this.attempts.length, this.tries);
    }

    submit(attempt) {
        const guess = attempt.options.map(option => option.textContent)
        // check if the value is found or correct in the answer
        attempt.value = guess.map(check(this.answer))

        attempt.choices.forEach((choice, i) => {
            choice.disabled = true;
            if (attempt.value[i] == 2) {
                choice.setAttribute("correct", "");
                choice.setAttribute("part", "choice choice-correct");
            } else if (attempt.value[i] == 1) {
                choice.setAttribute("found", "");
                choice.setAttribute("part", "choice choice-found");
            }
        });
        attempt.options.forEach((option, i) => {
            option.disabled = this.guidance && !attempt.value[i]
        })
        if (this.for) {
            this.for.value = guess.join("")
            this.for.form && this._replay || this.for.form.submit()
        }
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
        this.shadowRoot.removeChild(this.progress);
    }

    push(option) {
        option.disabled = true;
        this.attempt.options.push(option);
        this.choose(option, this.attempt);
        if (this.attempt.options.length == 4) {
            if (this.submit(this.attempt)) this.finish(true);
            else if (this.attempts.length == this.tries) this.finish(false);
            else this.attempts.push(this.attempt = {
                options: [],
                choices: [],
            });
            this.updateProgress(this.attempts.length, this.tries);
        }
        return this.options.assignedElements().indexOf(option);
    }
    select(event) {
        const { target: option } = event
        if (option.slot === 'option') {
            this.cache.append(this.push(option))
        }
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
        
        this.progress = document.createElement("span");

        this.shadowRoot.append(
            slot,
            this.options,
            this.progress,
            this.choices,
            this.success,
            this.failure,
        );
    }

    pop(option, choice) {
        option.disabled = false;
        this.attempt.options.splice(this.attempt.options.indexOf(option), 1);
        this.choices.removeChild(choice);
        return this.options.assignedElements().indexOf(option);
    }

    choose(option) {
        const choice = document.createElement("button");
        choice.classList.add("choice");
        choice.setAttribute("part", "choice");
        choice.textContent = option.textContent;
        const remove = () => this.cache.remove(this.pop(option, choice))
        choice.addEventListener("click", remove)
        this.attempt.choices.push(choice);
        this.choices.append(choice);
    }
}

class Cache {

    touched = false;

    constructor(id) {
        this.id = id;
    }

    append(value) {
        const { data } = this; // Load data
        data.push(value);
        this.data = data; // Save data
    }

    remove(value) {
        let { data } = this; // Load data
        let item = data.splice(data.lastIndexOf(value), 1);
        this.data = data; // Save data
        return item;
    }

    clear() {
        localStorage.removeItem(this.id);
    }

    set data(value) {
        localStorage.setItem(this.id, JSON.stringify(value));
    }

    get data() {
        return JSON.parse(localStorage.getItem(this.id)) || [];
    }

    *[Symbol.iterator]() {
        for (let item of this.data) {
            yield item
        }
        this.touched = true;
    }

}

customElements.define('selection-puzzle', SelectionPuzzle);