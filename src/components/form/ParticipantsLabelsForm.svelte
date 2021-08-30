<script lang="ts">
	import { createForm } from 'svelte-forms-lib';
	import * as yup from 'yup';
	import { getContext } from 'svelte';
	import { participants, labels } from '../../utils/stores';

	const { close } = getContext('simple-modal');

	export let index;
	export let resourceId;
	export let resourceType;
	export let formMethod;

	function getInitialName() {
		console.log(index);
		if (index !== undefined) {
			return resourceType == 'participants' ? $participants[index].name : $labels[index].name;
		} else {
			return '';
		}
	}

	const { form, errors, handleChange, handleSubmit, isValid, isSubmitting } = createForm({
		initialValues: {
			name: getInitialName()
		},
		validationSchema: yup.object().shape({
			name: yup.string().required()
		}),
		onSubmit: () => {
			if (resourceId !== undefined) {
				return formMethod(resourceId, resourceType, $form)
					.then((response) => {
						if (resourceType == 'participants') {
							$participants[index] = response.data;
						} else {
							$labels[index] = response.data;
						}
						close();
					})
					.catch((error) => alert(error));
			} else {
				return formMethod(resourceType, $form).then((response) => {
					if (resourceType == 'participants') {
						$participants = [...$participants, response.data];
					} else {
						$labels = [...$labels, response.data];
					}
					close();
				});
			}
		}
	});
</script>

<h2>Edit {resourceType == 'participants' ? 'Participant' : 'Label'} Data</h2>

<form on:submit={handleSubmit}>
	<label for="name">name</label>
	<input name="name" on:change={handleChange} on:blur={handleChange} bind:value={$form.name} />
	{#if $errors.name}
		<small>{$errors.name}</small>
	{/if}

	<button type="submit" disabled={!$isValid}>
		{#if $isSubmitting}
			sending request...
		{:else}
			submit
		{/if}
	</button>
</form>

<style>
	:root {
		--primary-light: #a6f9d6;
		--primary: #5be2a9;
		--primary-dark: #53ce9a;
		--secondary: #1e2145;
		--white: #fff;
		--grey: #e6e6ff;
		--grey-dark: #6d7098;
		--red: #ff6b6b;
	}

	input {
		font-family: inherit;
		font-size: inherit;
		max-width: 400px;
		width: 100%;
		padding: 12px;
		box-sizing: border-box;
		border: 1px solid var(--grey);
		border-radius: 4px;
		transition: all 150ms ease;
		background: var(--white);
	}

	input:focus {
		outline: none;
		box-shadow: 0 0 0 4px rgb(227, 227, 245);
		border-color: var(--grey);
	}

	input:disabled {
		color: #ccc;
	}

	button {
		color: #fff;
		background-color: var(--primary);
		border: none;
		text-transform: uppercase;
		letter-spacing: 1.8px;
		outline: none;
		border-radius: 4px;
		display: block;
		margin-top: 12px;
		line-height: 1.8;
		font-size: 12px;
		padding: 10px 18px;
		min-width: 120px;
		transition: all 150ms ease;
		cursor: pointer;
	}

	button:disabled {
		background-color: var(--grey);
	}

	button:focus:not(:disabled) {
		box-shadow: 0 0 0 4px var(--primary-light);
	}

	button:hover:not(:disabled) {
		background-color: var(--primary-dark);
	}

	label {
		display: block;
		color: var(--grey-dark);
		font-weight: bold;
		margin-top: 20px;
		margin-bottom: 4px;
		text-transform: uppercase;
		font-size: 12px;
		letter-spacing: 1.9px;
		line-height: 2;
	}

	/* used for errors */
	small {
		display: block;
		font-size: 12px;
		color: var(--red);
		margin-top: 10px;
	}
</style>
