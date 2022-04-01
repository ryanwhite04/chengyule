
async function select(path, secret=0) {
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
        .split('').sort().join('');
    return {
        answer: selections[0],
        options,
    }
}

select('chengyu.json').then(({ answer, options }) => {
    const puzzle = document.getElementById('puzzle');
    puzzle.setAttribute('answer', answer.chinese);
    puzzle.setAttribute('options', options);
    puzzle.setAttribute('question', answer.english);
}).catch(console.error)




