// check('abcd')('x', 1) == 0 // not found
// check('abcd')('a', 1) == 1 // found but not correct
// check('abcd')('b', 1) == 2 // correct
function check(string) {
    return (v, i) => string.includes(v) ? string[i] == v ? 2 : 1 : 0;
}

export default class SelectionPuzzle extends HTMLElement {

    static get observedAttributes() {
        return [
            "for",
            "cache", // int: whether or not to save progress
            "tries", // int: how many tries they get
            "answer", // string: the solution
            "disable-incorrect", // boolean: whether or not to hide wrong choices
        ]
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
        } else if (name == "tries" && newValue) {
            this.tries = parseInt(newValue);
            this.updateProgress(this.attempts.length, this.tries);
        } else if (name == "cache") {
            this.cache = parseInt(newValue);
        } else if (name == "for") {
            this.input = newValue && document.getElementById(newValue);
        } else {
            this[name] = newValue;
        }
    }

    updateProgress(attempts, tries) {
        const remaining = tries-attempts;
        this.progress.textContent = `You have ${1+remaining} ${remaining ? "tries" : "try"} left`;
    }

    tries = 4;
    state = "playing";

    attempt = {
        options: [],
        choices: [],
    };
    disableIncorrect = false;

    replay(history) {
        this._replay = true;
        const options = this.options.assignedElements();
        for (let index of history) {
            this.push(options[index])
        }
        this._replay = false;
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
        this.history = new History(this.getAttribute("history"))
        this.history.cache = this.cache;
        this.replay(this.history)
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
            option.disabled = this.disableIncorrect && !attempt.value[i]
        })
        if (this.input) {
            this.input.value = guess.join("")
            this.input.form && this._replay || this.input.form.submit()
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
            this.history.append(this.push(option))
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
        const remove = () => this.history.remove(this.pop(option, choice))
        choice.addEventListener("click", remove)
        this.attempt.choices.push(choice);
        this.choices.append(choice);
    }
}

class History {

    constructor(history) {
        this._data = JSON.parse(history) || [];
    }

    set cache(cache) {
        this._cache = cache;
        cache ? this.load() : this.clear();
    }

    get cache() {
        return this._cache;
    }

    toString() {
        return JSON.stringify(this._data);
    }

    append(value) {
        this._data.push(value);
        this.save();
    }

    remove(value) {
        const index = this._data.lastIndexOf(value);
        let item = this._data.splice(index, 1);
        this.save();
        return item;
    }

    clear() {
        localStorage.removeItem(this._cache);
    }

    save() {
        this._cache && localStorage
            .setItem(this._cache, JSON.stringify(this._data));
    }

    load() {
        this._data = (this._cache &&
            JSON.parse(localStorage.getItem(this._cache))) ||
            this._data;
    }

    *[Symbol.iterator]() {
        for (let item in this._data) {
            yield item
        }
    }

}

customElements.define('selection-puzzle', SelectionPuzzle);