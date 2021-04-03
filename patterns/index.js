const patternDict = [{
    pattern: '\\b(hi|hello|hey)\\b',
    intent: 'Hello'
},{
    pattern: '\\b(bye|exit|goodbye)\\b',
    intent: 'Exit'
},{
    pattern: '\\b(who|author|creator)\\b',
    intent: 'Author'
},{
    pattern: '\\bmake\\sme\\sa\\splaylist\\b',
    intent: 'Playlist'
},{
    pattern: '\\b(?<time>[0-9]+)\\sminutes\\b',
    intent: 'Time'
},{
    pattern: '\\bpublic\\skey\\s\\b(?<pkey>[A-Za-z0-9]+)\\b',
    intent: 'Pkey'
},{
    pattern: '\\bprivate\\skey\\s\\b(?<skey>[A-Za-z0-9]+)\\b',
    intent: 'Skey'
},{
    pattern: '\\bplaylist\\sid\\s\\b(?<pid>[A-Za-z0-9:\/.]+)\\b',
    intent: 'Pid'
}];
module.exports = patternDict;