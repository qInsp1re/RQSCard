document.addEventListener('DOMContentLoaded', () => {
    console.log("Web3 Interface Loaded");

    if (typeof window.ethereum !== 'undefined') {
        console.log('MetaMask is installed!');
        const web3 = new Web3(window.ethereum);

        // Запрос баланса и других данных
        // Пример вызова функции контракта для получения баланса
        async function getBalance() {
            const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
            const account = accounts[0];
            const balance = await web3.eth.getBalance(account);
            document.getElementById('balance').innerText = web3.utils.fromWei(balance, 'ether') + ' ETH';
        }

        getBalance();
    } else {
        console.log('MetaMask is not installed');
    }
});
