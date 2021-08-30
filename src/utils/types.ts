export interface Meeting {
	id: number;
	name: string;
	data_started: Date;
	date_ended: Date;
	link: string;
}

export interface Participant {
	id: number;
	name: string;
}

export interface Label {
	id: number;
	name: string;
}
