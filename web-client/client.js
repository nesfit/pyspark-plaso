
class ApiClient {

	API_ROOT = 'https://gort.fit.vutbr.cz/pp/';


	async getLs(hdfsPath) {
		const response = await fetch(this.API_ROOT + 'ls' + hdfsPath);
		return await response.json();
	}

	downloadFile(hdfsPath) {
		fetch(this.API_ROOT + 'file' + hdfsPath)
			.then(resp => resp.blob())
			.then(blob => {
				const url = window.URL.createObjectURL(blob);
				const a = document.createElement('a');
				a.style.display = 'none';
				a.href = url;
				// the filename you want
				//a.download = 'todo-1.json';
				document.body.appendChild(a);
				a.click();
				window.URL.revokeObjectURL(url);
			})
			.catch(() => alert('Could not download ' + hdfsPath));
	}

	fileLink(hdfsPath) {
		return this.API_ROOT + 'file' + hdfsPath;
	}

	zipLink(hdfsPath) {
		return this.API_ROOT + 'zip' + hdfsPath;
	}

}
