

export default class CountDown extends HTMLElement {

    static get observedAttributes() {
        return [
            'time'
        ]
    }

    constructor() {
        super();
        this.attachShadow({mode: 'open'}); // sets and returns 'this.shadowRoot'

        const wrapper = document.createElement('span');
        wrapper.setAttribute('class','wrapper');

        const icon = wrapper.appendChild(document.createElement('span'));
        icon.setAttribute('class','icon');
        icon.setAttribute('tabindex', 0);

        const img = icon.appendChild(document.createElement('img'));
        img.src = this.hasAttribute('img') ? this.getAttribute('img') : 'img/default.png';

        const info = wrapper.appendChild(document.createElement('span'));
        info.setAttribute('class','info');
        info.textContent = this.getAttribute('data-text');

        this.shadowRoot.append(this.style, wrapper);
    }

    get style() {
        const tag = document.createElement('style');
        tag.textContent = `
        .wrapper {
            background: blue;
            border: solid 4px red;
        }
        `;
        return tag;
    }

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

customElements.define('count-down', CountDown);