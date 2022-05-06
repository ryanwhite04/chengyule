export async function select(path, secret=0) {
    // const period = 1000*60*60*24;
    const period = 1000*10;
    const key = Math.floor(Date.now()/period)+secret;
    const encoder = new TextEncoder();
    const digest = await crypto.subtle.digest('SHA-256', encoder.encode(key))
    const dataView = new DataView(digest, 0);
    const chengyu = await fetch(path).then(body => body.json());
    const selections = [];
    for (let i = 0; i < 4; i++) {
        selections.push(chengyu[dataView.getUint16(i*2)%chengyu.length])
    }
    const options = selections
        .reduce((string, selection) => string + selection.chinese, '')
        .split('').sort();
    return {
        answer: selections[0],
        options,
    }
}

export function change(puzzle) {
    return ({ answer, options }) => {
        puzzle.setAttribute('answer', answer.chinese);
        puzzle.innerHTML = `<h2/>${answer.english}</h2>`;
        puzzle.append(options.reduce((fragment, option) => {
            const button = document.createElement('button');
            button.textContent = option;
            button.setAttribute('slot', 'option');
            fragment.append(button);
            return fragment;
        }, document.createDocumentFragment()));
    }
}
