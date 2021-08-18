import {Button, Card, Col, Container, FormControl, InputGroup, Row, Spinner} from "react-bootstrap";
import React from "react";

export default function EditCard({loading, title, children, onSave = () => undefined}) {
    return (
        <Container>
            <Row className="mb-5"/>
            <Card>
                <Card.Header>
                    <Row>
                        <h5 className="ml-2">{title}</h5>
                        {loading ?
                            <Spinner animation="border" variant="info" className="ml-auto mr-2"/> : ""
                        }
                    </Row>
                </Card.Header>
                <Card.Body>
                    <Row>
                        {children}
                    </Row>
                </Card.Body>
                <Card.Footer>
                    <Button variant="info" className="pr-5 pl-5 float-right" onClick={onSave}>Save</Button>
                </Card.Footer>
            </Card>
        </Container>
    )
}

EditCard.Input = function ({title, value, setValueFunc}) {
    return (
        <Col md={4} className="pt-2">
            <InputGroup>
                <InputGroup.Prepend>
                    <InputGroup.Text>
                        {title}
                    </InputGroup.Text>
                </InputGroup.Prepend>
                <FormControl
                    value={value}
                    onChange={e => setValueFunc(e.target.value)}/>
            </InputGroup>
        </Col>
    )
}