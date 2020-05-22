
class ApiClient {

	// there can be some issues with a relative URL, see https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Cross-global_fetch_usage
	API_ROOT = './api/';


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

	extractLink(hdfsPath) {
		return this.API_ROOT + 'extract' + hdfsPath;
	}

	async uploadFile(hdfsPath, formData) {
		const url = this.API_ROOT + 'file' + hdfsPath + formData.name;
		const response = await fetch(url, {
			method: 'POST',
			body: formData
		});
		return await response.text();
	}

	async uploadZip(hdfsPath, formData) {
		const url = this.API_ROOT + 'zip' + hdfsPath;
		const response = await fetch(url, {
			method: 'POST',
			body: formData
		});
		return await response.text();
	}

	mkdir(hdfsPath, dirname) {
		const url = this.API_ROOT + 'file' + hdfsPath + dirname;
		fetch(url, { method: 'POST' })
			.then()
			.catch((error) => console.error(error));
	}

	rmdir(hdfsPath) {
		const url = this.API_ROOT + 'rm' + hdfsPath;
		fetch(url)
			.then()
			.catch((error) => console.error(error));
	}

	rm(hdfsFilePath) {
		const url = this.API_ROOT + 'rm' + hdfsFilePath;
		fetch(url)
			.then()
			.catch((error) => console.error(error));
	}

	async runExport(hdfsPath) {
		const response = await fetch(this.API_ROOT + 'extract-to-halyard' + hdfsPath);
		return await response.text();
	}

}
